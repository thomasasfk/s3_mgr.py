import boto3
import argparse
import os.path
import botocore
import sys


def setup_arguments():
    """ setup argparse arguments """
    
    # setup parser and group
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group()
    
    # add arguments
    group.add_argument("-l", "--list", help="list files available on s3", action="store_true")
    group.add_argument("-u", "--upload", dest="path_of_image_to_upload", help="upload image file from path to s3")
    group.add_argument("-d", "--download", dest="file_to_download", help="download image file from s3 to cwd")
    parser.add_argument("-n", "--name", dest="name_of_file",
                        help="name for file to be uploaded/downloaded as (optional)", default="null")

    # exit it no arguments
    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        sys.exit(2)

    return parser.parse_args()


def check_exists_in_s3(object_name):
    """ check an objects existence in the s3 bucket """
    s3 = boto3.resource('s3')

    try:
        s3.Object('cloud-platform-bucket', object_name).load()
        return True
    except botocore.exceptions.ClientError:
        return False


def check_exists_in_db(object_name):
    """ check an objects existence in dynamodb table """
    dynamodb = boto3.resource("dynamodb")
    table = dynamodb.Table("image-labels")

    return "Item" in table.get_item(Key={"image": object_name})


def list_objects(continuation_token=None, page_number=1):
    """ list objects in the s3 bucket """
    s3_client = boto3.client('s3')

    if continuation_token is None:
        response = s3_client.list_objects_v2(
            Bucket='cloud-platform-bucket',
            MaxKeys=10,
            Prefix='images',
            RequestPayer='requester'
        )
    else:
        response = s3_client.list_objects_v2(
            Bucket='cloud-platform-bucket',
            MaxKeys=10,
            Prefix='images',
            ContinuationToken=continuation_token,
            RequestPayer='requester'
        )

    status_code = response["ResponseMetadata"]["HTTPStatusCode"]
    if status_code == 200:
        if "Contents" in response:
            contents = response["Contents"]
            print("Page {}".format(page_number))
            for image in contents:
                print("   {}".format(image["Key"][7:]))
            if "NextContinuationToken" in response:
                if input("View next page? (y/N): ").lower() == "y":
                    list_objects(response["NextContinuationToken"], page_number + 1)
        else:
            print("No files currently exist in s3")

    else:
        print("Error, status code: {}".format(status_code))


def upload_image(image_path, custom_name_inf):
    """ upload image to the s3 bucket, custom name is optional """
    s3_client = boto3.client('s3')
    file_name_inf = os.path.basename(image_path)

    try:
        # set format_string to custom name if one exists
        format_string = "images/{}".format(file_name_inf if custom_name_inf == '' else custom_name_inf)
        # format for output
        format_print_string = "as '{}'".format(custom_name_inf) if custom_name_inf != '' else ''
        s3_client.upload_file(image_path, "cloud-platform-bucket", format_string)

        print("Image '{}' successfully uploaded {}".format(file_name_inf, format_print_string))
        return True
    except boto3.exceptions.S3UploadFailedError:
        print("Error uploading, unauthorized file type")
    return False


def download_image(file_to_download, custom_name_inf):
    """ download an image from the s3 bucket to cwd, custom name is optional """
    s3_resource = boto3.resource('s3')

    try:
        # set format_string to custom name if one exists
        format_string = os.path.basename(custom_name_inf) if custom_name_inf != '' else file_to_download
        # format for output
        format_print_string = "as '{}'".format(custom_name_inf) if custom_name_inf != '' else ''
        s3_resource.Bucket("cloud-platform-bucket").download_file("images/{}".format(file_to_download), format_string)
        print("Image '{}' successfully downloaded {}".format(file_to_download, format_print_string))
        return True
    except botocore.exceptions.ClientError as e:
        if e.response['Error']['Code'] == "404":
            print("Image '{}' doesn't exist in s3".format(args.file_to_download))
    return False


if __name__ == "__main__":
    args = setup_arguments()

    custom_name = os.path.basename(args.name_of_file) if args.name_of_file != 'null' else ''

    # --list
    if args.list:
        list_objects()

    # --upload
    elif args.path_of_image_to_upload is not None:
        # set the name the file will be downloaded as
        file_name = custom_name if custom_name != '' else os.path.basename(args.path_of_image_to_upload)
        if os.path.isfile(args.path_of_image_to_upload):
            # if the file and labels don't exist in the cloud
            if not check_exists_in_db(file_name) and not check_exists_in_s3(file_name):
                upload_image(args.path_of_image_to_upload, custom_name)
            else:
                choice = input("'{}' already exists on s3, override? (y/N): ".format(file_name))
                if choice.lower() == "y":
                    upload_image(args.path_of_image_to_upload, custom_name)
                else:
                    print("Cancelled upload of file '{}' to s3".format(file_name))

        else:
            print("Image '{}' doesn't exist in specified path".format(file_name))

    # --download
    elif args.file_to_download is not None:
        # strip filename from path, just incase
        file_name_s3 = os.path.basename(args.file_to_download)
        file_name = custom_name if custom_name != '' else file_name_s3
        if not os.path.isfile(file_name):
            download_image(file_name_s3, custom_name)
        else:
            choice = input("'{}' already exists in cwd, override? (y/N): ".format(file_name))
            if choice.lower() == "y":
                download_image(file_name_s3, custom_name)
            else:
                print("Cancelled download of file '{}'".format(file_name))
