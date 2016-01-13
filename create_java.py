#!/usr/bin/python
#encoding=utf-8

import os
import sys
import unicodedata
import MySQLdb as mysql

import config
import db_config


from string import Template


#下划线命名格式驼峰命名格式
def underline_to_camel(underline_format):

    camel_format = ''
    if type(underline_format)==unicode:
        underline_format = unicodedata.normalize('NFKD',underline_format).encode('utf-8','ignore')
    if isinstance(underline_format, str):
        for _s_ in underline_format.split('_'):
            camel_format += _s_.capitalize()
    return camel_format

#根据数据库的表自动生成jpa文件
def jpaProduceModel(parameters,results):
    if not os.path.exists(parameters[2]):
        os.mkdir(parameters[2])
    jpamodelClass(parameters,results)

def produceService(parameters,results):
    serviceInter(parameters,results)
    serviceImpl(parameters,results)

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
    code = Template('''package\n
@Entity
@Table(name="${tableName}")
public class ${className}  implements Serializable{\n
${attribute}
${methods}
}''')
    name = parameters[0]    # class name
    argv2 = parameters[1]
    path = parameters[2]
    attribute = ""
    methods = ""

    for x in results:
        propName = x[0]
        propType = dbtype(x[1])
        propNameCamel = underline_to_camel(x[0])
        attribute += "\t@Column(name='" + propName + "');\n\tprivate " + propType + " " + propNameCamel +";\n\n"
        methods += "\tpublic " + propType + " get" + propNameCamel + "() {\n\t\treturn " + propNameCamel + ";\n\t}\n\n"
        methods += "\tpublic void set" + propNameCamel + "(" + propType + " " + propNameCamel + ") {\n\t\tthis." + \
                   propNameCamel + " = " + propNameCamel + ";\n\t}\n\n"

    fileStr = code.substitute(tableName=db_config.Table, className=name, attribute=attribute, methods=methods)
    saveFile(fileStr, path + '/' + name+".java")

def serviceInter(parameters,results):
    code = Template('''package
public interface ${name}Service {
    /**
	 * 创建
${param_notes}
	 * @return ${name}信息
	 */
    public ${name} create${name}(${param});

    /**
	 * 查询全部
	 * @return 全部${name}列表
	 */
	public List<${name}> findAll${name}s();

	/**
	 * 根据${column_first_name}查询${name}信息
	 * @param ${column_first_type} ${column_first_name}
	 * @return ${name}信息
	 */
	public ${name} findUserByName(${column_first_type} ${column_first_name});

	/**
	 * 删除一个${name}
	 * @param ${column_first_type} ${column_first_name}
	 */
	public void remove${name}(${column_first_type} ${column_first_name});

	/**
	 * 修改一个${name}
	 * @param ${column_first_type} ${column_first_name}
	 */
	public void update${name}(${column_first_type} ${column_first_name});
}
''')
    name = parameters[0]
    path = parameters[2]
    param_notes = ""
    param = ""
    column_first_name = ""
    column_first_type = ""
    column_first_bool = True
    for x in results:
        propName = x[0]
        propType = dbtype(x[1])
        propNameCamel = underline_to_camel(x[0])
        if column_first_bool:
            column_first_name = propNameCamel.encode("utf-8")
            column_first_type = propType
            column_first_bool = False
        param_notes += "\t * @param " + propType + " " + propNameCamel + "\n"
        if param!="":
            propType = "," + propType
        param += propType + " " + propNameCamel
    fileStr = code.substitute(name=name,param_notes=param_notes,param=param,column_first_name=column_first_name,column_first_type=column_first_type)
    saveFile(fileStr, path + '/' + name+"Service.java")

def serviceImpl(parameters,results):
    code = Template('''package\n
@Service
public class ${name}ServiceImpl implements ${name}Service{

    @Resource
    private ${name}Dao ${namelow}Dao;

    /**
	 * 创建
${param_notes}
	 * @return ${name}信息
	 */
    public ${name} create${name}(${param}){

    }

    /**
	 * 查询全部
	 * @return 全部${name}列表
	 */
	public List<${name}> findAll${name}s(){

	}

	/**
	 * 根据${column_first_name}查询${name}信息
	 * @param ${column_first_type} ${column_first_name}
	 * @return ${column_first_type} ${column_first_name}信息
	 */
	public ${name} findUserByName(${column_first_type} ${column_first_name}){

	}

	/**
	 * 删除一个${name}
	 * @param ${column_first_type} ${column_first_name}
	 */
	public void remove${name}(${column_first_type} ${column_first_name}){

	}

	/**
	 * 修改一个${name}
	 * @param ${column_first_type} ${column_first_name}
	 */
	public void update${name}(${column_first_type} ${column_first_name}){

	}
}
''')
    name = parameters[0]
    namelow = name.lower()
    path = parameters[2]
    param_notes = ""
    param = ""
    column_first_name = ""
    column_first_type = ""
    column_first_bool = True
    for x in results:
        propName = x[0]
        propType = dbtype(x[1])
        propNameCamel = underline_to_camel(x[0])
        if column_first_bool:
            column_first_name = propNameCamel.encode("utf-8")
            column_first_type = propType
            column_first_bool = False
        param_notes += "\t * @param " + propType + " " + propNameCamel + "\n"
        if param!="":
            propType = "," + propType
        param += propType + " " + propNameCamel
    fileStr = code.substitute(name=name,namelow=namelow,param_notes=param_notes,param=param,column_first_name=column_first_name,column_first_type=column_first_type)
    saveFile(fileStr, path + '/' + name+"ServiceImpl.java")

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
        results = connectDb()
        jpaProduceModel(parameters,results)
        produceService(parameters,results)
        #produceDao(parameters)

if __name__ == "__main__":
    main()