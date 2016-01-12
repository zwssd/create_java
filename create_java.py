#!/usr/bin/python
#encoding=utf-8

import os
import sys
import MySQLdb as mysql

import config
import db_config


from string import Template

#根据数据库的表自动生成jpa文件
def jpaModel(parameters):
    if not os.path.exists(parameters[2]):
        os.mkdir(parameters[2])
    results = connectDb()
    jpamodelClass(parameters,results)

def produceModel(parameters):
    print(parameters[2])
    if not os.path.exists(parameters[2]):
        os.mkdir(parameters[2])
    modelClass(parameters)
    defModelHBM(parameters)

def produceService(parameters):
    serviceInter(parameters)
    serviceImpl(parameters)

def produceDao(parameters):
    daoInter(parameters)
    daoImpl(parameters)

def connectDb():
    print 'show columns from %s'%db_config.Table
    connect = mysql.connect(user=db_config.User,passwd=db_config.Passwd,host=db_config.Host,db=db_config.Db,charset='utf8').cursor()
    connect.execute('show columns from %s'%db_config.Table)
    results=connect.fetchall()
    return results

def dbtype(db_column_type):
    if "int" in db_column_type:
        val = "int"
    elif "char" in db_column_type:
        val = "String"
    elif "text" in db_column_type:
        val = "String"
    return val

def jpamodelClass(parameters,results):
    code = Template('''''package\n
@Entity
@Table(name="${tableName}")
public class ${className}  implements Serializable{\n
${attribute}
${methods}
}
''')
    name = parameters[0]    # class name
    argv2 = parameters[1]
    attribute = ""
    methods = ""

    for x in results:
        propName = x[0]
        propType = dbtype(x[1])
        attribute += "\t@Column(name='" + propName + "');\n\tprivate " + propType + " " + propName +";\n\n"
        methods += "\tpublic " + propType + " get" + propName + "() {\n\treturn " + propName + ";\n\t}\n\n"
        methods += "\tpublic void set" + propName + "(" + propType + " " + propName + ") {\n\tthis." + propName + " = " + propName + ";\n\t}\n\n"

    '''properties = argv2.split(",")
    for x in range(len(properties)):
        prop = properties[x].split(":")
        propType = prop[1]
        propName = prop[0]
        attribute += "\tprivate " + propType + " " + propName + ";\n"
        methods += "\tpublic "+propType+" set"+propName.capitalize()+"("+propType+" "+propName+") {\n\t\tthis."+propName+" = " + propName + ";\n\t}\n"
        methods += "\tpublic void get"+propName.capitalize()+"() {\n\t\treturn "+propName+";\n\t}\n"'''

    fileStr = code.substitute(tableName=db_config.Table, className=name, attribute=attribute, methods=methods)
    saveFile(fileStr, parameters[2] + '/' + name+".java")

def modelClass(parameters):
    code = Template('''''package\n
public class ${className} {\n
${attribute}
${methods}
}
''')
    name = parameters[0]    # class name
    argv2 = parameters[1]
    attribute = ""
    methods = ""
    properties = argv2.split(",")
    for x in range(len(properties)):
        prop = properties[x].split(":")
        propType = prop[1]
        propName = prop[0]
        attribute += "\tprivate " + propType + " " + propName + ";\n"
        methods += "\tpublic "+propType+" set"+propName.capitalize()+"("+propType+" "+propName+") {\n\t\tthis."+propName+" = " + propName + ";\n\t}\n"
        methods += "\tpublic void get"+propName.capitalize()+"() {\n\t\treturn "+propName+";\n\t}\n"

    fileStr = code.substitute(className=name, attribute=attribute, methods=methods)
    saveFile(fileStr, parameters[2] + '/' + name+".java")

def defModelHBM(parameters):
    code = Template('''''
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE hibernate-mapping PUBLIC
    "-//Hibernate/Hibernate Mapping DTD 3.0//EN"
    "http://hibernate.sourceforge.net/hibernate-mapping-3.0.dtd">

<hibernate-mapping>
    <class name="${name}" table="${name}">
${property}
    </class>
</hibernate-mapping>
''')
    name = parameters[0]    # class name
    argv2 = parameters[1]
    property = ""
    properties = argv2.split(",")
    for x in range(len(properties)):
        prop = properties[x].split(":")
        property += "\t\t<property name=\""+prop[0]+"\" />\n"

    fileStr = code.substitute(name=name, property=property)
    saveFile(fileStr, parameters[2] + '/' + name+".hbm.xml")

def serviceInter(parameters):
    code = Template('''''package\n
public interface ${name}Service extends GenericManager<${name}, Integer> {

}
''')
    name = parameters[0]
    fileStr = code.substitute(name=name)
    saveFile(fileStr, parameters[2] + '/' + name+"Service.java")

def serviceImpl(parameters):
    code = Template('''''package\n
public class ${name}ServiceImpl extends GenericManagerImpl<${name}, Integer>
        implements ${name}Service{

    private ${name}Dao ${namelow}Dao;

    public ${name}ServiceImpl(${name}Dao ${namelow}Dao){
        super(${namelow}Dao);
        this.${namelow}Dao = ${namelow}Dao;
    }
}
''')
    name = parameters[0]
    namelow = name.lower()
    fileStr = code.substitute(name=name, namelow=namelow)
    saveFile(fileStr, parameters[2] + '/' + name+"ServiceImpl.java")

def daoInter(parameters):
    code = Template('''''package\n
public interface ${name}Dao extends GenericDao<${name}, Integer> {

}
''')
    name = parameters[0]
    fileStr = code.substitute(name=name)
    saveFile(fileStr, parameters[2] + '/' + name+"Dao.java")

def daoImpl(parameters):
    code = Template('''''package\n
public class ${name}ServiceImpl extends GenericManagerImpl<${name}, Integer>
        implements ${name}Service{

    private ${name}Dao ${namelow}Dao;

    public ${name}ServiceImpl(${name}Dao ${namelow}Dao){
        super(${namelow}Dao);
        this.${namelow}Dao = ${namelow}Dao;
    }
}
''')
    name = parameters[0]
    namelow = name.lower()
    fileStr = code.substitute(name=name, namelow=namelow)
    saveFile(fileStr, parameters[2] + '/' + name+"DaoImpl.java")

def saveFile(code, path):
    print path
    f = open(path,'w')
    f.write(code)
    f.close()

#param1 ModelName
#param2 Properties
#param3 Path
def main():
    parameters = [config.Name,config.Parameters,config.Path]    # class name
    number = len(parameters)
    if (number < 2):
        print "Error parameters"
    else :
        jpaModel(parameters)
        #produceModel(parameters)
        #produceService(parameters)
        #produceDao(parameters)

if __name__ == "__main__":
    main()