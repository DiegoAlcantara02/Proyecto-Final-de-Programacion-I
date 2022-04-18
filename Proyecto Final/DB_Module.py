import sqlite3, os, traceback, string
from datetime import datetime
import PySimpleGUI as sg
sg.theme("DarkAmber")
sg.set_options(font=("Times New Roman", 16))
database = "Vacunados.db"
con = sqlite3.connect(database)
cursor = con.cursor()
table="Vacunados"
margins=(10,10)

columns={
	"ID":"INTEGER PRIMARY KEY AUTOINCREMENT",
	"Nombre":"text", 
	"Apellido":"text", 
	"Teléfono":"Text",
	"Fecha_de_nacimiento":"Date",
	"Tipo_de_Vacuna_1":"text",
	"Provincia_1":"text",
	"Fecha_1":"Date",
	"Tipo_de_Vacuna_2":"text",
	"Provincia_2":"text",
	"Fecha_2":"Date",
	"Tipo_de_Vacuna_3":"text",
	"Provincia_3":"text",
	"Fecha_3":"Date",
	}
provfile="Prov.config"
vacfile="Vac.config"
lista_provincias=[
"Azua "
"Banoruco",
"Barahona",
"Dajabón",
"Distrito Nacional",
"Duarte",
"El seibo",
"Elias Piña",
"Espaillat",
"Hato Mayor",
"Hermanas Mirabal",
"Independencia",
"La Altagracia",
"La Romana",
"La Vega",
"María Trinidad Sánchez",
"Monseñor Nouel",
"Monte Cristi",
"Monte Plata",
"Pedernales",
"Peravia",
"Puerto Plata",
"Samaná",
"San Cristóbal",
"San José de Ocoa",
"San Juan",
"San Pedro de Macorís",
"Santiago",
"Santiago Rodríguez",
"Santo Domingo",
"Sánchez Ramírez",
"Valverde"
]

lista_vacunas=[
"Sinovac (Coronavac)",
"Pfizer/BioNTech (Cominarty)",
"SII (Covishield)",
"Aztrazeneca (AZD122)",
"Johnson & Johnson (Janssen/Ad26.COV2.S)",
"Moderna (mRNA-1273)",
"CNBG (Sinophar"
]
def getquery(query):
	try:
		cursor.execute(query)
		return cursor.fetchall()
		con.commit()
	except Exception as e:
		return []
		tb = traceback.format_exc()
		print(f"ERROR:", e, tb)

def setquery(query, confirm):
	try:
		num_rows=int()
		if any(word in query for word in ["INSERT", "UPDATE", "DELETE"]):
			num_rows+=cursor.execute(query).rowcount
		else:
			cursor.execute(query)

		if bool(confirm):
			con.commit()
		else:
			con.rollback()

		return num_rows
	except Exception as e:
		tb = traceback.format_exc()
		print(f"ERROR:", e, tb)

def CreateTable():
	query="CREATE TABLE IF NOT EXISTS {} (".format(table)
	for x,column in enumerate(columns):
		if x+1==len(columns):
			query+="{} {})".format(column, columns[column])
		else:
			query+="{} {}, ".format(column, columns[column])
	setquery(query, 1)

def DropTable():
	setquery("DROP TABLE IF EXISTS {}".format(table), 1)


CreateTable()

def Select_All():
	return getquery("SELECT * FROM "+table)

def Del_ALL():
	return setquery("DELETE *FROM "+table)

def Select_Where(value_condition):
	return getquery("SELECT *FROM {} WHERE ID = '{}'".format(table, value_condition))[0]
	
def getIDs():
	results = getquery("SELECT ID FROM "+table)
	ids=list()
	for row in results:
		ids.append(row[0])
	return ids

def Insert_Row(list_of_values):
	if len(list_of_values)>1:
		return setquery("INSERT INTO {} ({}) VALUES {}".format(table,
		", ".join(list(columns)[1:len(columns)]), tuple(list_of_values)), 1)
	else:
		return setquery("INSERT INTO {} ({}) VALUES {}".format(table,
		", ".join(list(columns)[1:len(columns)]), str(tuple(list_of_values)).replace(",", "")), 1)


def Delete_where(ID):
	return setquery("DELETE FROM {} WHERE ID='{}'".format(table, ID), 1)

def Update(columns_values, ID):
	values=str(columns_values)
	changes={
	":":"=",
	"{":"",
	"}":"",
	",":",\n"
	}
	for change in changes:
		values=values.replace(change, changes[change])
	return setquery("UPDATE {} SET\n {} WHERE ID='{}'".format(table, values, ID), 1)


def get_List(lista):
	if "vac" in lista.lower():
		if os.path.exists(vacfile):
			with open(vacfile, "r", encoding="UTF-8") as vacunas:
				return vacunas.read().split(sep="\n")
		else:
			with open(vacfile, "w", encoding="UTF-8") as vacunas:
				vacunas.write("\n".join(lista_vacunas))
				return lista_vacunas

	elif "prov" in lista.lower():
		if os.path.exists(provfile):
			with open(provfile, "r", encoding="UTF-8") as provincias:
				return provincias.read().split(sep="\n")
		else:
			with open(provfile, "w", encoding="UTF-8") as provincias:
				provincias.write("\n".join(lista_provincias))
				return lista_provincias
	else:
		return []


def valid_String(string_text):
	if str(string_text).isspace() or (str(string_text) in string.whitespace):
		return False
	elif bool(string_text):
		return True
	else:
		return False

def validate(string):
	try:
		date = datetime.strptime(string, "%a %d/%m/%Y")
	except Exception as e:
		tb=traceback.format_exc()
		print(f"ERROR: ", e, tb)
		return False
	else:
		return True
