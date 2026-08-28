import base64

local_pic = r"D:\PythonProgram\PythonProject\2026.8.22\shopkeeper_brain\knowledge\test\import\img\test.jpg"

with open(local_pic, "rb") as img:
    print(base64.b64encode(img.read()).decode("utf-8"))
