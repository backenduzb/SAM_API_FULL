import aiohttp
from data.config import url_edit_teacher

async def get_teacher_status(teacher_id):
    edited_url = f"{url_edit_teacher}{teacher_id}"

    async with aiohttp.ClientSession() as session:
        async with session.get(edited_url) as response:
            status_data = await response.json()

    juda_yaxshi = status_data.get("juda_ham_qoniqaman")
    yaxshi = status_data.get("ortacha_qoniqaman")
    ortacha = status_data.get("asosan_qoniqaman")
    past = status_data.get("qoniqmayman")
    yomon = status_data.get("umuman_qoniqaman")

    if status_data:
        return f"<b>⭐️ Sizga yangi status belgilandi!</b>\n<pre> Juda yaxshi - {juda_yaxshi} \n Yaxshi - {yaxshi} \n O'rtacha - {ortacha} \n Past - {past} \n Yomon {yomon}</pre>"
