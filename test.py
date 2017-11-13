import wd_languages as wd



a = wd.User_LanguageObjectIDType("User_Language_ID", "fr_FR")

with open("test.xml", "w") as f:
    a.export(f, 0)
