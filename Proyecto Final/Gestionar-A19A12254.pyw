from DB_Module import *

def GestForm():
	column_rows=list()
	for x,column in enumerate(columns):
		column_rows.append([sg.T(column+":", pad=(1,6))])
		if column=="ID":
			column_rows[x].append(sg.Spin(getIDs(), size=50, readonly=True, key=column,
			enable_events=True, background_color=sg.theme_input_background_color()))

		elif columns[column]=="Date":
			column_rows[x]+=[sg.In(key=column, size=38), sg.CalendarButton("Escoger Fecha", format="%a %d/%m/%Y")]

		elif any(val in column for val in ["Provincia", "Tipo_de_Vacuna"]):
			column_rows[x]+=[sg.Combo(get_List(column), key=column, size=(50,10))]

		else:
			column_rows[x].append(sg.In(key=column, size=51))
	rows=Select_All()
	tabs={
	"Gestionar Vacunados":[
	[sg.Col(column_rows+
	[
	[sg.Checkbox("Limpiar Campos Automáticamente", key="Auto_Clean", default=True),
	sg.BM("Opciones de Registro", ["Menu", [op + " Registro" for op in ["Agregar", "Actualizar", "Borrar"]]], key="CRUD")]
	], element_justification="r", justification="l"), sg.Multiline(size=(40	,30), visible=False)],
	],
	"Visualizar Vacunados":[
	[sg.Table(rows, headings=list(columns), auto_size_columns=bool(rows),  num_rows=23,
	col_widths=[len(col) for col in columns], justification="c", vertical_scroll_only=False,
	key=table, bind_return_key=True)]
	]
	}
	
	layout=[
	[sg.TabGroup(
		[[sg.Tab(tab, tabs[tab], element_justification="r")] for tab in tabs]
		)
	],
	]
	try:
		def Valid_Obligated_Fields():
			valid=bool(1)
			for x,column in enumerate(list(columns)[1:5]):
				if columns[column] in ("Text", "text") and not valid_String(datavac[column]):
					windowvac[column](background_color = "red")
					sg.popup_error("Error, El campo {} se encuentra vacío".format(column))
					windowvac[column](background_color = sg.theme_input_background_color())
					valid = not valid
					break

				elif columns[column]=="Date" and not validate(datavac[column]):
					windowvac[column](background_color = "red")
					sg.popup_error("Error, El formato de fecha del campo {} no es válido".format(column))
					windowvac[column](background_color = sg.theme_input_background_color())
					valid = not valid

			return valid

		def valid_vac():
			valid=bool(1)
			vac_cols=list(column.replace("1", "") for column in list(columns)[5:8])
			for x in range(1,4):
				if x>=1 and all(not valid_String(datavac[col+str(x)]) for col in vac_cols):
					pass
				else:
					for col in vac_cols:
						if not valid_String(datavac[col+str(x)]):
							windowvac[col+str(x)](background_color="red")
							sg.popup_error("Error, el campo {} se encuentra vacío.".format(col+str(x)))
							windowvac[col+str(x)](background_color=sg.theme_input_background_color())
							valid=not valid
							break

						elif columns[col+str(x)]=="Date" and not validate(datavac[col+str(x)]):
							windowvac[col+str(x)](background_color="red")
							sg.popup_error("Error, el formato de Fecha del campo {} no es válido.".format(col+str(x)))
							windowvac[col+str(x)](background_color=sg.theme_input_background_color())
							valid = not valid
							break

						elif "Fecha" not in col and datavac[col+str(x)] not in windowvac[col+str(x)].Values:
							sg.popup_error("Error,  en el campo {}. El valor especificado no se encuentra en la lista".format(col+str(x)))
							valid = not valid
							break
			return valid

		def Refresh():
			ids=getIDs()
			windowvac['ID'](values=getIDs(), value=ids[0])
			windowvac[table](values=Select_All())

		windowvac=sg.Window("Formulario de Vacunados", layout, margins=(10,10), resizable=True,
		element_justification="c", enable_close_attempted_event=True, finalize=True)
		windowvac.Maximize()
		while True:
			eventvac, datavac = windowvac.read()

			if eventvac not in ("Salir", "-WINDOW CLOSE ATTEMPTED-"):
				if eventvac=="ID":
					row=Select_Where(datavac["ID"])
					for x,elem in enumerate(row):
						windowvac[list(columns)[x]](elem)

				elif eventvac==table:
					row=windowvac[table].get()[datavac[table][0]]
					for x,column in enumerate(columns):
						windowvac[column](row[x])

				elif eventvac=="CRUD":

					if "Agregar" in datavac[eventvac]:
						if not Valid_Obligated_Fields():
							pass
						
						elif not valid_vac():
							pass
						
						else:
							Insert_Row(tuple(datavac[column] for column in list(columns)[1:len(columns)]))
							Refresh()

					elif any(val in datavac[eventvac] for val in ["Borrar", "Actualizar"]) and datavac["ID"] not in windowvac["ID"].Values:
						sg.popup_error("Error, la ID en el campo ID no existe.")
					
					elif "Borrar" in datavac[eventvac]:
						if sg.popup_yes_no("¿Desea Eliminar este registro?")=="Yes":
							Delete_where(datavac["ID"])
							sg.popup_ok("Registro Eliminado")
							Refresh()

					elif "Actualizar" in datavac[eventvac]:
						if sg.popup_yes_no("¿Confirmar Actualización?")=="Yes":
							Update(dict(zip(list(columns)[1:len(columns)], list(datavac[column] for column in list(columns)[1:len(columns)]))), datavac["ID"])
							sg.popup_ok("Registro Actualizado")
							Refresh()
					
					if bool(datavac["Auto_Clean"]):
						for column in list(columns)[1:len(columns)]:
							windowvac[column]("")
			else:
				if sg.popup_yes_no("Desea cerrar el programa?")=="Yes":
					windowvac.close()
					break


	except Exception as e:
		tb=traceback.format_exc()
		sg.popup_error_with_traceback("Error:", e, tb)
	else:
		pass

if __name__ == '__main__':
	try:
		GestForm()
	except Exception as e:
		tb=traceback.format_exc()
		print(e, tb)
	