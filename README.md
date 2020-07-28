# Arguments and Usage
## Usage
```
usage: s3_mgr.py [-h] [-l | -u PATH_OF_IMAGE_TO_UPLOAD | -d FILE_TO_DOWNLOAD] 
                 [-n NAME_OF_FILE]
```
## Arguments
### Quick reference table
|Short|Long        |Default|Description                                       |
|-----|------------|-------|--------------------------------------------------|
|`-h` |`--help`    |       |show this help message and exit                   |
|`-l` |`--list`    |       |list files available on s3                        |
|`-u` |`--upload`  |`None` |upload image file from path to s3                 |
|`-d` |`--download`|`None` |download image file from s3 to cwd                |
|`-n` |`--name`    |`null` |filename to be uploaded/downloaded as (optional)|

### `-h`, `--help`
show this help message and exit

### `-l`, `--list`
list files available on s3

### `-u`, `--upload` (Default: None)
upload image file from path to s3

### `-d`, `--download` (Default: None)
download image file from s3 to cwd

### `-n`, `--name` (Default: null)
name for file to be uploaded/downloaded as (optional)
