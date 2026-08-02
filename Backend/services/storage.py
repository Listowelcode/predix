import os
import uuid

from dotenv import load_dotenv

from supabase import create_client



# =====================================
# LOAD ENVIRONMENT VARIABLES
# =====================================

load_dotenv()



SUPABASE_URL = os.getenv(
    "SUPABASE_URL"
)


SUPABASE_KEY = os.getenv(
    "SUPABASE_SERVICE_KEY"
)




# =====================================
# CHECK ENV VARIABLES
# =====================================

if not SUPABASE_URL:

    raise Exception(
        "SUPABASE_URL missing in .env file"
    )



if not SUPABASE_KEY:

    raise Exception(
        "SUPABASE_SERVICE_KEY missing in .env file"
    )





# =====================================
# SUPABASE CLIENT
# =====================================

supabase = create_client(

    SUPABASE_URL,

    SUPABASE_KEY

)





# =====================================
# STORAGE BUCKET
# =====================================

BUCKET_NAME = "predix-logos"







# =====================================
# UPLOAD IMAGE
# =====================================

def upload_image(

    file,

    filename,

    content_type

):


    try:


        # remove spaces

        filename = filename.replace(
            " ",
            "_"
        )



        # get extension

        if "." in filename:

            extension = filename.split(
                "."
            )[-1]

        else:

            extension = "png"





        # generate unique filename

        unique_filename = (

            str(uuid.uuid4())

            +

            "."

            +

            extension

        )





        # storage path

        path = (

            "matches/"

            +

            unique_filename

        )





        # upload

        supabase.storage.from_(

            BUCKET_NAME

        ).upload(

            path,

            file,

            {

                "content-type":
                content_type,

                "upsert":
                False

            }

        )





        # public url

        public_url = (

            SUPABASE_URL

            +

            "/storage/v1/object/public/"

            +

            BUCKET_NAME

            +

            "/"

            +

            path

        )




        return public_url





    except Exception as e:


        raise Exception(

            f"Image upload failed: {str(e)}"

        )








# =====================================
# DELETE IMAGE
# =====================================

def delete_image(

    image_url

):


    try:


        if not image_url:

            return





        # extract storage path

        path = image_url.split(

            f"{BUCKET_NAME}/"

        )[-1]





        supabase.storage.from_(

            BUCKET_NAME

        ).remove(

            [

                path

            ]

        )





    except Exception as e:


        raise Exception(

            f"Image deletion failed: {str(e)}"

        )