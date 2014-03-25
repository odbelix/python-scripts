#!/usr/bin/python
# -*- coding: utf-8 -*-
import psycopg2
import sys


con = None

try:
     
    con = psycopg2.connect(host='190.110.100.78', database='db_lms_pregrado', user='u_lms_utal',password="u_lms_moodle_12") 

    result = "RUT;ESTADO;CURSO;ESTADO\n"
    result_course = ""
    result_username = ""
    result_username_info = ""

    file_query_username = open("query_user.txt","w")
    file_query_course = open("query_course.txt","w")
    file_result = open("check_cursos-2014-1.csv","w")
    
    file_username_info = open("username_info.csv","w")

    username_list = []

    #Read a file
    file_data = open(sys.argv[1],'r')
    for line in file_data:
        data = str.split(line,";")
        course = data[0]
        username = data[2].replace("\n","")
        
        #QUERY USERNAME
        query_user = "SELECT count(*) from mdl_user WHERE username='%s'" %(username)
        result_username = result_username + query_user +"\n"
        cur = con.cursor()
        cur.execute(query_user)          
        ver = cur.fetchone()
        result = result+username+";"
        if ver[0] == 1:
            result = result+"ACTIVO;"
            if username not in username_list:
                username_list.append(username)
                query_username_info = "select username,email,firstname,lastname from mdl_user where username='%s'" % (username)
                cur = con.cursor()
                cur.execute(query_username_info)
                var = cur.fetchone()
                result_username_info = result_username_info+var[0]+";"+var[1]+";"+var[2]+";"+var[3]+"\n"
            
        else:
            result = result+"INACTIVO/NOCREADO;"
        
        
        #QUERY_COURSE
        query_course = "SELECT COUNT(*) from mdl_course WHERE shortname='%s'" %(course)
        result_course = result_course + query_course + "\n"
        cur = con.cursor()
        cur.execute(query_user)          
        ver = cur.fetchone()
        result = result+course+";"
        if ver[0] == 1:
            result = result+"ACTIVO;"
        else:
            result = result+"INACTIVO/NOCREADO;"

        result = result+"\n"

    file_username_info.write(result_username_info)
    file_query_username.write(result_username)
    file_query_course.write(result_course)
    file_result.write(result)
    

    file_username_info.close()
    file_query_username.close()
    file_query_course.close()
    file_result.close()
    file_data.close()

except psycopg2.DatabaseError, e:
    print 'Error :%s' % e    
    sys.exit(1)
    
    
finally:
    
    if con:
        con.close()
