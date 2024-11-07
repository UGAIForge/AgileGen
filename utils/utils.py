import os
import zipfile


def zip_folder(folder_path, output_path):
    with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                file_path = os.path.join(root, file)
                zip_file.write(file_path, os.path.relpath(file_path, folder_path))



def iframe_generator(file_path):
    iframe = """
        <iframe src="file={0}" id="bi_iframe" width="100%" height="500px" onload="adjustIframe();"></iframe>
        <script>
        function adjustIframe(){{
            var ifm= document.getElementById("bi_iframe");
            ifm.height=document.documentElement.clientHeight;
            ifm.width=document.documentElement.clientWidth;
        }}
        </script>
        """.format(file_path)
    
    return iframe