import requests
from pprint import pp
import json
import os
from tqdm import tqdm
import yt_dlp


def scrape():
    url = "https://api.learning.dnc.group/study-plan/filter/content/65"
    dnc_data = {"modulos": []}
    headers = {
        "accept": "application/json, text/plain, */*",
        "origin": "https://learning.dnc.group",
        "referer": "https://learning.dnc.group/",
        "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
    }

    courses = requests.get(url=url, headers=headers).json()
    course_id = 0
    for course in tqdm(courses):
        module_id = course["step_id"]
        base_course_url = (
            f"https://api.learning.dnc.group/player/7052/step/{course['step_id']}"
        )
        videos_data = requests.get(url=base_course_url, headers=headers).json()

        video_id_g = 0
        for content in videos_data:
            s3_video_url = content["content_url"]
            module_title = content["step_title"]
            video_title = content["content_title"]
            summary = content["content_smart_player_summary"]
            zips = content.get("content_material_url")

            path = os.path.join(
                os.getcwd(),
                "dnc",
                str(course_id) + " " + module_title.strip(),
                str(video_id_g) + " " + video_title.strip(),
            )

            if not os.path.exists(path):
                os.makedirs(path)

            if ".pdf" in s3_video_url:
                html_template_pdf = f"""
                    <!DOCTYPE html>
                    <html lang="pt-BR">
                        <head>
                            <meta charset="UTF-8">
                            <meta name="viewport" content="width=device-width, initial-scale=1.0">
                            <title>{module_title}</title>
                            <!-- Tailwind CSS via CDN -->
                            <script src="https://cdn.tailwindcss.com"></script>
                        </head>
                        <body class="bg-gray-900 min-h-screen">
                            <div class="container mx-auto px-4 py-8">
                                <!-- Header -->
                                <header class="mb-8">
                                    <div class="flex items-center gap-2 text-3xl mb-2">
                                        <span class="text-gray-400">{module_title}</span>
                                        <span class="text-gray-600">/</span>
                                        <span class="text-white font-semibold">{video_title}</span>
                                    </div>
                                </header>

                                <!-- PDF Embed Container -->
                                <div class="relative w-full bg-black rounded-lg shadow-lg overflow-hidden mb-8">
                                    <!-- Embed PDF directly in the page -->
                                    <embed src="{s3_video_url}" type="application/pdf" width="100%" height="800px">
                                </div>

                                <!-- Summary Section -->
                                <div class="bg-gray-800 rounded-lg p-6 mt-8 shadow-lg text-white">
                                    {summary}
                                </div>
                            </div>
                        </body>
                    </html>
            """
                with open(os.path.join(path, "index_pdf2.html"), "w") as f:
                    f.write(html_template_pdf)

            else:
                html_template = f"""
                <!DOCTYPE html>
                <html lang="pt-BR">
                    <head>
                        <meta charset="UTF-8">
                        <meta name="viewport" content="width=device-width, initial-scale=1.0">
                        <title>{video_title}</title>
                        <!-- Tailwind CSS via CDN -->
                        <script src="https://cdn.tailwindcss.com"></script>
                    </head>
                    <body class="bg-gray-900 min-h-screen">
                        <div class="container mx-auto px-4 py-8">
                            <!-- Header -->
                            <header class="mb-8">
                                <div class="flex items-center gap-2 text-3xl mb-2">
                                    <span class="text-gray-400">{module_title}</span>
                                    <span class="text-gray-600">/</span>
                                    <span class="text-white font-semibold">{video_title}</span>
                                </div>
                            </header>

                            <!-- Video Player Container -->
                            <div class="relative w-full aspect-w-16 aspect-h-9 bg-black rounded-lg shadow-lg overflow-hidden mb-8">
                                <video 
                                    class="w-full h-full object-contain"
                                    controls
                                    controlsList="nodownload"
                                    poster=""
                                >
                                    <source src="{s3_video_url}" type="video/mp4">
                                    <p class="text-white text-center p-4">Seu navegador não suporta a tag de vídeo.</p>
                                </video>
                            </div>
                            <div class="text-pink-400">
                                <a href="{zips}">Materiais</a>
                            </div>
                            <!-- Summary Section -->
                            <div class="bg-gray-800 rounded-lg p-6 mt-8 shadow-lg text-white">
                                {summary}
                            </div>
                        </div>
                    </body>
                </html>
                 """
                with open(os.path.join(path, "index.html"), "w") as f:
                    f.write(html_template)

            if module_title not in [
                module.get("titulo") for module in dnc_data["modulos"]
            ]:
                dnc_data["modulos"].append(
                    {
                        "titulo": f"{str(course_id)} {module_title.strip()}",
                        "videos": [],
                    }
                )
            for module in dnc_data["modulos"]:
                if module["titulo"] == f"{str(course_id)} {module_title.strip()}":
                    module["videos"].append(
                        {
                            "titulo": f"{video_id_g} {video_title.strip()}",
                            "url": f"{s3_video_url}",
                        }
                    )
            video_id_g += 1
            with open("data.json", "w") as f:
                json.dump(
                    dnc_data,
                    f,
                    ensure_ascii=False,
                    indent=4,
                )

            yt_opts = {
                "format": "best",
                "outtmpl": os.path.join(
                    path,
                    "video.%(ext)s",
                ),
            }
            """ 
            ydl = yt_dlp.YoutubeDL(yt_opts)

            try:
                ydl.download(s3_video_url)
            except Exception as e:
                print(f"form")
            """

        course_id += 1


if __name__ == "__main__":
    pp("...Starting...")
    scrape()
