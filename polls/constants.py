englandDict = ["Buckinghamshire","Cambridgeshire","Cumbria","Derbyshire","Devon","Dorset","East Sussex","Essex","Gloucestershire","Hampshire","Hertfordshire","Kent","Lancashire","Leicestershire","Lincolnshire","Norfolk","North Yorkshire","Northamptonshire","Nottinghamshire","Oxfordshire","Somerset","Staffordshire","Suffolk","Surrey","Warwickshire","West Sussex","Worcestershire","London, City of","Barking and Dagenham","Barnet","Bexley","Brent","Bromley","Camden","Croydon","Ealing","Enfield","Greenwich","Hackney","Hammersmith and Fulham","Haringey","Harrow","Havering","Hillingdon","Hounslow","Islington","Kensington and Chelsea","Kingston upon Thames","Lambeth","Lewisham","Merton","Newham","Redbridge","Richmond upon Thames","Southwark","Sutton","Tower Hamlets","Waltham Forest","Wandsworth","Westminster","Barnsley","Birmingham","Bolton","Bradford","Bury","Calderdale","Coventry","Doncaster","Dudley","Gateshead","Kirklees","Knowsley","Leeds","Liverpool","Manchester","Newcastle upon Tyne","North Tyneside","Oldham","Rochdale","Rotherham","St. Helens","Salford","Sandwell","Sefton","Sheffield","Solihull","South Tyneside","Stockport","Sunderland","Tameside","Trafford","Wakefield","Walsall","Wigan","Wirral","Wolverhampton","Bath and North East Somerset","Bedford","Blackburn with Darwen","Blackpool","Bournemouth","Bracknell Forest","Brighton and Hove","Bristol, City of","Central Bedfordshire","Cheshire East","Cheshire West and Chester","Cornwall","Darlington","Derby","Durham","East Riding of Yorkshire","Halton","Hartlepool","Herefordshire","Isle of Wight","Isles of Scilly","Kingston upon Hull","Leicester","Luton","Medway","Middlesbrough","Milton Keynes","North East Lincolnshire","North Lincolnshire","North Somerset","Northumberland","Nottingham","Peterborough","Plymouth","Poole","Portsmouth","Reading","Redcar and Cleveland","Rutland","Shropshire","Slough","South Gloucestershire","Southampton","Southend-on-Sea","Stockton-on-Tees","Stoke-on-Trent","Swindon","Telford and Wrekin","Thurrock","Torbay","Warrington","West Berkshire","Wiltshire","Windsor and Maidenhead","Wokingham","York"];

nothernIreLand = ['Antrim','Ards','Armagh','Ballymena','Ballymoney','Banbridge','Belfast','Carrickfergus','Castlereagh','Coleraine','Cookstown','Craigavon','Derry','Down','Dungannon and South Tyrone','Fermanagh','Larne','Limavady','Lisburn','Magherafelt','Moyle','Newry and Mourne District','Newtownabbey','North Down','Omagh','Strabane'];

scotland = ["Aberdeen City","Aberdeenshire","Angus","Argyll and Bute","Clackmannanshire","Dumfries and Galloway","Dundee City","East Ayrshire","East Dunbartonshire","East Lothian","East Renfrewshire","Edinburgh, City of","Eilean Siar","Falkirk","Fife","Glasgow City","Highland","Inverclyde","Midlothian","Moray","North Ayrshire","North Lanarkshire","Orkney Islands","Perth and Kinross","Renfrewshire","Scottish Borders, The","Shetland Islands","South Ayrshire","South Lanarkshire","Stirling","West Dunbartonshire","West Lothian"];

wales = ["Blaenau Gwent","Bridgend","Caerphilly","Cardiff","Carmarthenshire","Ceredigion","Conwy","Denbighshire","Flintshire","Gwynedd","Isle of Anglesey","Merthyr Tydfil","Monmouthshire","Neath Port Talbot","Newport","Pembrokeshire","Powys","Rhondda, Cynon, Taff","Swansea","Torfaen","Wrexham","Vale of Glamorgan, The"];

regionDict = {
	"IN":"India","AZ":"Azerbaijan","US":"USA","PK":"Pakistan","GB":"United Kingdom","AU":"Australia","CA":"Canada","PH":"Philippines","AQ":"Antartica","BB":"Barbados","DE":"Germany","SJ":"Svalbard","AF":"Afghanistan","DZ":"Algeria","AL":"Albania","AS":"American Samoa","AO":"Angola","AI":"Anguilla","AG":"Antigua and Barbuda","AR":"Argentina","AM":"Armenia","AW":"Aruba","AT":"Austria","AZ":"Azerbaijan","BS":"Bahamas","BH":"Bahrain","BD":"Bangladesh","BB":"Barbados","BY":"Belarus","BE":"Belgium","BZ":"Belize","BJ":"Benin","BR":"Brazil","BM":"Bermuda","BT":"Bhutan","BO":"Bolivia","BA":"Bosnia and Herzegovina","CN":"China","DE":"Germany","DK":"Denmark","NL":"Netherlands","PK":"Pakistan","ZW":"Zimbabwe","ZM":"Zambia","ZA":"South Africa","CH":"Switzerland","TH":"Thailand","SG":"Singapore","SE":"Sweden","TR":"Turkey","QA":"Qatar","RE":"Reunion","RO":"Romania","SA":"Saudi Arabia","RW":"Rwanda","JP":"Japan","KE":"Kenya","NO":"Norway","NP":"Nepal","PL":"Poland","NZ":"New Zealand","GB-SCT":"Scotland","EG":"Egypt"
}

gender_excel_dic = {
	"M":1,
	"F":2,
	"D":3
}

prof_excel_dic = {
	"Student":1,
	"Politics":2,
	"Education":3,
	"Information Technology":4,
	"Public Sector":5,
	"Social Services":6,
	"Medical":7,
	"Finance":8,
	"Manager":9,
	"Others":10
}

age_excel_dic ={
	1:"Upto 19",
	2:"20 - 25",
	3:"26 - 30",
	4:"31 - 35",
	5:"36 - 50",
	6:"50+"
}

import xlwt
normal_style = xlwt.easyxf(
	"""
	font:name Verdana
	"""
)

border_style = xlwt.easyxf(
	"""
	font:name Verdana;
	border: top thin, right thin, bottom thin, left thin;
	align: vert centre, horiz left;
	"""
)