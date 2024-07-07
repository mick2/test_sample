此文档主要分为三个主目录，对应生成三份使用手册：kg_sdk_man(cli 手册)、kg_sdk_sample(测试用例手册)、kg_sdk_doc(SDK 每个功能模块说明)。

开发人员在开发功能时，需要及时更新自己的开发模块：

1、kg_sdk_doc/doc：创建自己的模块说明文件，格式如 example.md，
kg_sdk_doc/src：存放模块说明文件的图片;

2、kg_sdk_sample/doc：测试用例的增删改查
kg_sdk_sample/src: 用例相关图片的修改

3、kg_sdk_cli：CLI 修改
kg_sdk_api/sdk_api：API 修改

4、执行./gen_sdk_doc.sh 生成 kg_sdk_doc.chm;
执行./gen_sdk_man.sh 生成 kg_sdk_man.chm;
执行./gen_sdk_sample.sh 生成 kg_sdk_sample.chm;

Note :

1. 数字序号乱序问题，当在数字序号下一行输入 `*`时，要在 `*`前面敲入 `Tab`键，否则会出现数字序号乱序。
2. 由MarkDown生成chm文件时，不支持中文目录，即 `##`标题语法后面要用英文写。
3. 全文只能有一个一级标题。
4. 插入图片的格式 `![](xxx.png)`,不要使用 `![](../src/xxx.png)`,否则生成的chm文件图片格式错误。
5. markdown换行需要输入两个空格后按enter，直接按enter不会换行

出版本：
1. git pull
2. ./copy_api.sh 更新代码中的cli 更新api手册