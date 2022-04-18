from DB_Module import *
lastquery="SELECT *FROM "+table
operadores={
	"Como":"LIKE",
	"Igual a":"=",
	"Mayor que":">",
	"Menor que":"<",
	"En la lista":"IN",
	"Entre":"BETWEEN",
	"Diferente de":"!=",
	"Mayor o Igual que":">=",
	"Menor o Igual que":"<="
}
def GestForm():
	global lastquery
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
	menu_def=["Menu",
	["Ordenar", "Refrescar", "Buscar"]
	]
	tabs={
	"Gestionar Vacunados":[
	[sg.Column(column_rows+
	[
	[sg.Checkbox("Limpiar Campos Automáticamente", key="Auto_Clean", default=True),
	sg.BM("Opciones de Registro", ["Menu", [op + " Registro" for op in ["Agregar", "Actualizar", "Borrar"]]], key="CRUD")]
	], element_justification="r", justification="l"), sg.Multiline(size=(40	,30), visible=False)],
	],
	"Visualizar Vacunados":[
	[sg.Table(rows, headings=list(columns), auto_size_columns=bool(rows),  num_rows=23,
	col_widths=[len(col) for col in columns], justification="c", vertical_scroll_only=False,
	key=table, bind_return_key=True, right_click_menu=menu_def)]
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
			windowvac[table](values=getquery(lastquery))
			ids=list(row[0] for row in windowvac[table].get())
			windowvac['ID'](values=ids, value=ids[0])

		windowvac=sg.Window("Formulario de Vacunados", layout, margins=(margins), resizable=True,
		element_justification="c", enable_close_attempted_event=True, finalize=True)
		windowvac.Maximize()
		while True:
			eventvac, datavac = windowvac.read()
			print(eventvac)
			if eventvac not in ("Salir", "-WINDOW CLOSE ATTEMPTED-"):
				if eventvac=="ID":
					row=Select_Where(datavac["ID"])
					for x,elem in enumerate(row):
						windowvac[list(columns)[x]](elem)

				elif eventvac==table:
					row=windowvac[table].get()[datavac[table][0]]
					for x,column in enumerate(columns):
						windowvac[column](row[x])

				elif "Ordenar" in eventvac:
					lastquery=Order_By()
					if bool(lastquery):
						Refresh()
					else:
						lastquery="SELECT * FROM "+table

				elif "Refrescar" in eventvac:
					lastquery="SELECT * FROM "+table
					Refresh()

				elif "Buscar" in eventvac:
					results=Search()
					if bool(results):
						sg.popup_ok("La búsqueda a arrojado {} resultados".format(len(results)))
						Refresh()
					else:
						sg.popup_ok("Sin Resultados.")

				elif eventvac=="CRUD":
					if "Agregar" in datavac[eventvac]:
						if Valid_Obligated_Fields() and valid_vac():
							Insert_Row(tuple(datavac[column] for column in list(columns)[1:len(columns)]))
							sg.popup_ok("Registo Agregado.")
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

def Order_By():
	global lastquery
	layout=[
	[sg.Listbox(values=list(columns), size=(30,15), key="Columns", bind_return_key=True)],
	[sg.T("De forma:"), sg.InputOptionMenu(["Ascendente", "Descendente"], "Ascendente", size=(15,1), key="Asc_Dsc")],
	[sg.B('Ordenar'), sg.B('Cerrar Ventana')]
	]
	try:
		oevent, odata = sg.Window('Ordenar {} por'.format(table), layout, margins=(margins), element_justification='c', modal=True).read(close=True)
		if oevent in ("Ordenar", "Columns"):
			if bool(odata['Columns']):
				return "SELECT * FROM {} ORDER BY {} {}".format(table, odata['Columns'][0], odata["Asc_Dsc"][0:odata["Asc_Dsc"].find("c")+1])

			else:
				sg.popup_error("Error, no seleccionó ninguna columna")

	except Exception as e:
		sg.popup_error_with_traceback("AN EXCEPTION OCCURRED!", e, traceback.format_exc())


def Search():
	global lastquery
	layout=[
	[sg.T("Buscar en la columna:"), sg.InputOptionMenu(list(columns), "ID", key="Search_Column"),
	sg.T("Donde sea ")],
	[sg.InputOptionMenu(list(operadores.keys()), "Igual a", key="Operador"), sg.In("", key="Search", size=(20,1))],
	[sg.B(btn, bind_return_key=not bool(x)) for x,btn in enumerate(['Buscar', 'Cerrar Ventana'])]
	]
	try:
		bevent, bdata = sg.Window('Buscar en '+table, layout, margins=margins, element_justification='c', modal=True).read(close=True)
		
		if bevent=="Buscar":
			if valid_String(bdata['Search']):
				condition="'{}'".format(bdata['Search'])
				if "Como"==bdata['Operador']:
					condition=condition[0:len(condition)-1]+"%'"
				
				elif "En la lista" in bdata['Operador']:
					value=condition[condition.find("'")+1:len(condition)-1]
					valtupla = tuple(value.split(sep=','))
					if len(valtupla)>1:
						condition=condition.replace("'{}'".format(value), str(valtupla))
					else:
						condition=condition.replace("'{}'".format(value), str(valtupla).replace(",", ""))
				
				elif "Entre" in bdata['Operador']:
					value=condition[condition.find("'")+1:len(condition)-1]
					if len(value.split(sep=" y ")) != 2:
						num1, num2 = ("", "")
						show_error("Error en la condición. Cuando se usa el Operador entre,\n El formato correcto es: valor1 y valor2")
					else:
						num1, num2 = value.split(sep=" y ")

					condition=condition.replace("'{}'".format(value), "'{}' AND '{}'".format(num1, num2))

				lastquery=("SELECT * FROM {} WHERE {} {} {}").format(
				table, bdata['Search_Column'], operadores[bdata['Operador']], condition)

				return getquery(lastquery)
			else:
				show_error("Error, no especifico ningún valor.")
				return []
		else:
			return []


	except Exception as e:
		sg.popup_error_with_traceback("AN EXCEPTION OCCURRED!", e, traceback.format_exc())


if __name__ == '__main__':
	try:
		GestForm()
	except Exception as e:
		tb=traceback.format_exc()
		sg.popup_error_with_traceback("Error: ", e, tb)