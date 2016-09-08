# Jasper Deployment
---
Jasper Reports are being developed in jaspersoft server or iReports (deployed into server through publishing through the tool).

In case of migrating the reports to another jasper server, a deployment is followed.
As we are version controlling in git, we are suppose to clone from git and deploy through script, to overcome this manual deploy.

The following are the files to be uploaded
- **data source**
- **query**
- **input control**
- **reports**

#### Setup :
##### Manifest File :
The Whole deployment process is based on the `manifest.json` file.
The format of the manifest file to be as follows:

 `manifest.json`
```json
{
"jasper":
	{      "datasource":"datasource_name",
	       "reports":["Report_1",
      			"Report_2",
     			"Report_3",
     			"Report_4",
      			"Report_5"]
	}
}
```
##### jinja2 :
Jinja2 is one of the most used template engines for Python, widely used and secure with the optional sandboxed template execution environment. 

Run the command to install jinja2 into your machine :
```sh
sudo pip install jinja2
```

 ### Git Directory Structure :
The script works based on the folder structure as follows 
```
.
|
|___ deployment/
|       |___ helper_modules/
|       |      |___  templates/
|       |      |       |___ data_Source_res_desc.xml
|       |      |       |___ folder_res_desc.xml 
|       |      |       |___ inputcontrol_res_desc.xml
|       |      |       |___ query_res_desc.xml
|       |      |       |___ report_res_descr.xml
|       |      |___ create_folder.py
|       |      |___ datasource_upload.py
|       |      |___ inputcontrol_upload.py
|       |      |___ query_upload.py
|       |      |___ report_upload.py
|       |___ ReportDeployment.py
|       |___ config.json
|___ jasper
|       |___ deployment
|               |___ Datasource
|               |       |___ datasource_1
|               |___ Query
|               |       |___ query_1
|               |       |___ query_2
|               |       |___ ..
|               |___ Inputcontrol
|               |       |___ input_control_1
|               |       |___ ..
|               |___ Report
|                      |___ report_1
|                      |___ report_2
|                      |___ ..
..
```
The `ReportDeployment.py` file search for manifest file in `jasper/deployment/manifest.json`. If the manifest doesnt exit, we need to specify a path as

```ssh
export MANIFEST_PATH=XXX/XXXX/XXXX/manifest.json
```

#### Deployment Steps :
Pass the environment variables as parameters in terminal.
```sh
export JASPER_URL=http://XXXXXXXXX.com:8080/jasperserver
export JASPER_USER=XXXXXXXXXX
export JASPER_PASSWORD=XXXXXXXXXX
export REDSHIFT_URL=jdbc:postgresql://XXXXXXXXXX.redshift.amazonaws.com:5439
export REDSHIFT_USER=XXXXXXXXXX
export REDSHIFT_PASSWORD=XXXXXXXXXX
export REDSHIFT_DATABASE=XXXXXXXXXX
export PROJECT_NAME=XXXXXXXXXX
export MANIFEST_PATH=XXX/XXXX/XXXX/manifest.json
```

> * **REDSHIFT_URL** :
In case, if you are using any database other than redshift
then specify the particular connection URL.
> * **PROJECT_NAME** :
The name of the folder to be created in jasper server in which the reports are deployed.
> * **MANIFEST_PATH** :
The path of manifest file that specifies the report deployment details.
If already exists in `jasper/deployment/manifest.json` skip this step.

```sh
export DB_NAME=***********
export GIT_REPO_SRC=git@git.*****.com:*****/sample_repo.git
export GIT_BRANCH=*****
export GIT_REPO=sample_repo.git
# Get latest repo. 
cd
# Deletes directory if already exists
rm -rf $HOME/$DB_NAME
mkdir -p $HOME/$DB_NAME
cd $HOME/$DB_NAME
# Cloning git into local
git clone $GIT_REPO_SRC
cd $GIT_REPO
git checkout $GIT_BRANCH
cd $HOME/$DB_NAME/$GIT_REPO/deployment
# Running deployment script
python ReportDeployment.py
```
