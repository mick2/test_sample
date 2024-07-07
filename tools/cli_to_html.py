# @Author:chenjing
# @Date:2023/10/26

# /usr/bin/python
# -*- coding:utf-8 -*-

'''
提取cli文件中的cli命令及api生成网页格式显示
'''


import re
import os
import shutil


def macro_define(clidemopath):
    macro_dict = {}
    for macro_define_file in os.listdir(clidemopath):
        if '.h' in macro_define_file:
            with open('%s/%s'%(clidemopath,macro_define_file),'r',encoding='utf-8') as infile:
                lines = [line + '\n' for line in re.sub(r'\\\s*\n','',infile.read()).split('\n')]
                for line in lines:
                    if re.search(r'#define \w+.*"',line):
                        # print('define:',line)
                        key = re.findall(r'#define (\w+)',line)[0]
                        macro_dict[key] = re.findall(r'(".*")',line)[0]
                    elif re.search(r'#define \w+ ',line):
                        if '#define ' in line and '\\' not in line:
                            key = re.findall(r'define (\w+)', line)[0]
                            macro_dict[key] = re.sub(r'#define \w+','',line).strip()

    for key in macro_dict:
        if macro_dict[key] in macro_dict.keys():
            macro_dict[key] = macro_dict[macro_dict[key]]
    return macro_dict

def macro_replace(group,new_groups,cfile_macro_dict,common_macro_dict):
    group = re.sub(r'\\\s*\n',' ',group)
    new_group = ''
    for line in group.split('\n'):
        for var in re.findall(r'\w+',line):
            if var in cfile_macro_dict.keys():
                line = line.replace(var,cfile_macro_dict[var],1)
            if var in common_macro_dict.keys():
                line = line.replace(var, common_macro_dict[var], 1)
        new_group += line + '\n'
    new_groups.append(new_group)
    return new_groups


def get_funcs(group,module):
    func_group = ''
    func_list = re.findall(r'(kg_\w+)\(.*?\)', group)
    # print('func_list:', func_list)
    for func in list(set(func_list)):
        if func != 'cdl_cli_out':
            func_group += '<a href="group__%s.html#ga39e67eec2762d47c13282974de8c1e19" style="text-decoration:none" >%s</a>\n'%(module,func)
    return func_group


def get_cmd_para_list(group):
    cmd_para = re.findall(r'CDL_CLI\((.*?)\n{', group, re.S)[0].split('\n')
    # if '"' in re.findall(r'"(.*)"',cmd_para[2])[0]:
    #     for spara in re.findall(r'""(.*?)""',re.findall(r'"(.*)"',cmd_para[2])[0]):
    #         npara = spara.replace('|','--or--')
    #         cmd_para[2] = cmd_para[2].replace(spara,npara)
    cmd_para_list = [para.strip() for para in cmd_para[2].replace('(', ' ').replace(')', ' ').replace('{', ' ').replace('}', ' ').replace('"',' ').replace(',', ' ').replace('|',' ').split(' ') if para.strip() != '']
    cmdpara = re.findall(r'"(.*)"', cmd_para[2])[0].replace('"','')
    cmd_para_value = re.findall(r'"(.*?)",',''.join(cmd_para[3:]).replace('")','",'))
    if len(cmd_para_list) > len(cmd_para_value):
        cmd_para_value = cmd_para_value + ['ERR0R'] * (len(cmd_para_list) - len(cmd_para_value))
        # print('cmd_para1:', len(cmd_para), cmd_para)
    return cmdpara,cmd_para_list,cmd_para_value


def write_cdlcli_to_html(new_groups,htmlpath):
    with open(htmlpath,'w') as htmlfile:
        module = re.findall('kgxx_(.*?)_cli',htmlpath)[0]
        htmlfile.write('''
<head>
<meta http-equiv="Content-Type" content="text/xhtml;charset=UTF-8"/>
<title>Humber SDK </title>
<link href="tabs.css" rel="stylesheet" type="text/css"/>
<link href="search/search.css" rel="stylesheet" type="text/css"/>
<script type="text/javaScript" src="search/search.js"></script>
<link href="doxygen.css" rel="stylesheet" type="text/css"/>
</head>
<div class=header> <div class=headertitle> <h1>Chapter %s</h1>  </div> </div> <div class=contents>
'''%module.upper())
        for group in new_groups:

            func_group = get_funcs(group,module)
            cmdpara,cmd_para_list,cmd_para_value = get_cmd_para_list(group)
            htmlfile.write('\n\n<div class="memitem"> <div class="memproto"> <table width="%%100"> <tbody> <tr align=left"> <th  colspan=2 style="font-weight: bold; margin-left: 6px">%s</th> </tr> </tbody> </table> </div>  <div class="memdoc">  <table> <tbody>\n' % cmdpara)
            for i in range(len(cmd_para_list)):
                htmlfile.write('<tr><td width=22%% bgcolor=#e4d4ee>%s</td><td  bgcolor=#d4e4ee   width="1000">%s</td></tr>\n'%(cmd_para_list[i],cmd_para_value[i].replace('")','').replace('"','')))
            htmlfile.write('''<tr><td colspan=2   bgcolor=#eee4d4><pre><dl font-family="courier new"><dt><b>Related API:</b></dt><dd>
%s</dd></dl></pre></td></tr>
</tbody> </table> </div> </div>
'''%func_group)



def get_cfile_macro_dict(groups0):
    cfile_macro_dict = {}
    groups0 = groups0.replace('\\\n','')
    # print('groups0:',groups0)
    for line in groups0.split('\n'):
        if re.search(r'#define\s*\w+ ',line):
            # print('line:',line)
            key = re.findall(r'#define\s*(\w+)',line)[0]
            cfile_macro_dict[key] = re.sub(r'#define\s*\w+','',line).strip()
    for key in cfile_macro_dict:
        for var in re.findall(r'\w+', cfile_macro_dict[key]):
            if var in cfile_macro_dict.keys():
                cfile_macro_dict[key] = cfile_macro_dict[key].replace(var, cfile_macro_dict[var], 1)
    # print('cfile_macro_dict:',cfile_macro_dict)
    return cfile_macro_dict



def get_cfile(dlidemopath,common_macro_dict,clidemopath_html):
    module_file_list = []
    for file in os.listdir(dlidemopath):
        if '.c' in file:
            # print('file:',file)
            with open('%s/%s'%(dlidemopath,file),'r',encoding='utf-8') as infile:
                content = infile.read()
                content = re.sub(r'\\\s*\n',' ',content)
                content = re.sub(r'#define CDL_CLI\(.*?\n','',content)
                content = re.sub(r'#if 0.*?#endif','',content.replace('\n','huanhang')).replace('huanhang','\n')
                content = re.sub(r'//.*?\n', '', content)
                groups = content.split('CDL_CLI(')
                if '#define ' in groups[0]:
                    newgroup0 = macro_replace(groups[0],[],common_macro_dict,{})
                    # print('groups[0]:', newgroup0[0])
                    cfile_macro_dict = get_cfile_macro_dict(newgroup0[0])
                del groups[0]
                new_groups = []
                for group in groups:
                    group = re.sub(r'\\\s*\n',' ',group)
                    group = 'CDL_CLI(%s'%group
                    # print('group:',group)
                    new_groups = macro_replace(group,new_groups,cfile_macro_dict,common_macro_dict)
            # print('cfile_macro_dict:', cfile_macro_dict)
            # print('common_macro_dict:', common_macro_dict)
            write_cdlcli_to_html(new_groups,'%s/%s'%(clidemopath_html,file.replace('.c','.htm')))
            module_file_list.append(file.replace('.c','.htm'))
            # break
            with open('%s/%s' % (clidemopath_temp,file.replace('.c','_temp.c')),'w') as outfile:
                outfile.write(''.join(new_groups).replace('",','",\n'))
    return module_file_list



def make_dir(dirname):
    if not os.path.exists(dirname):
        os.mkdir(dirname)


def kgxx_guide(guidepath):
    with open(guidepath,'w') as outfile:
        outfile.write('''
<table border=0  height=100% width=100%>
    <tr>
        <td ><iframe frameborder=0 style="width:202;" name=_menu src=kgxx_guide_content.htm  height=100%></iframe></td>
        <td width=100%><iframe frameborder=0 style="width:100%;" name=_cli src=kgxx_guide_main.htm height=100% width=100%></iframe></td>
    </tr>
</table>
''')


def kgxx_guide_content(guide_content_path,module_file_list):
    ahref = ''
    for file in module_file_list:
        ahref += '<a href=%s target=_cli>%s</a><br>\n'%(file,re.findall('kgxx_(.*?)_cli',file)[0])
    with open(guide_content_path, 'w') as outfile:
        outfile.write('''
 <head> <meta http-equiv="Content-Type" cli_guide_content="text/xhtml;charset=UTF-8"/> <title>SDK CLI Content</title> </head> 
 <body style=background-color:#f2f2f2; > <h2> SDK CLI Guide</h2><br> <!--auto generated by csh script developed by Samuel Hu-->
<FONT FACE =Courier>
%s
</body>
'''%ahref)


def kgxx_guide_main(guide_main_path):
    with open(guide_main_path, 'w') as outfile:
        outfile.write('''
<head>
<meta http-equiv="Content-Type" content="text/xhtml;charset=UTF-8"/>
<title>HumberSDK: Main Page</title>
<link href="tabs.css" rel="stylesheet" type="text/css"/>
<link href="search/search.css" rel="stylesheet" type="text/css"/>
<script type="text/javaScript" src="search/search.js"></script>
<link href="doxygen.css" rel="stylesheet" type="text/css"/>
</head>

<br><br><br><h1>Command Line Interface (CLI) Guide</h1><br> 
<hr class="footer"/><address class="footer"><small>
  KG6524 SDK &#160;<a href="http://www.kgmicro.com/">
  <img class="footer" src="kgxx_log.png" alt="kgxx"/>
  </a> 1.1.0
  </small></address>
''')


if __name__ == '__main__':
    clidemopath = '../kg_sdk_cli'
    clidemopath_temp = '../kg_sdk_cli_temp'
    clidemopath_html = '../kg_sdk_man'
    guidepath = '%s/kgxx_guide.htm'%clidemopath_html
    guide_content_path = '%s/kgxx_guide_content.htm'%clidemopath_html
    guide_main_path = '%s/kgxx_guide_main.htm'%clidemopath_html
    make_dir(clidemopath_temp)
    make_dir(clidemopath_html)
    # macro_define_file = '%s/kgxx_cli_common.h'%clidemopath
    # macro_define_file1 = '%s/kgxx_cli.h'%clidemopath
    common_macro_dict = macro_define(clidemopath)
    # print('common_macro_dict:',common_macro_dict)
    module_file_list = get_cfile(clidemopath, common_macro_dict, clidemopath_html)
    kgxx_guide(guidepath)
    kgxx_guide_content(guide_content_path,module_file_list)
    kgxx_guide_main(guide_main_path)

