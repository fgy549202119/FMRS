from PIL import Image, ImageDraw, ImageFont
import os

media_dir = r'D:\bishe\FMRS\backend\media'

def create_placeholder_image(path, width, height, text, bg_color, text_color=(255, 255, 255)):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    img = Image.new('RGB', (width, height), bg_color)
    draw = ImageDraw.Draw(img)
    
    try:
        font = ImageFont.truetype("msyh.ttc", 40)
        small_font = ImageFont.truetype("msyh.ttc", 24)
    except:
        font = ImageFont.load_default()
        small_font = font
    
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    x = (width - text_width) // 2
    y = (height - text_height) // 2
    draw.text((x, y), text, fill=text_color, font=font)
    
    img.save(path, 'JPEG', quality=85)
    print(f"Created: {path}")

banner_colors = [
    (41, 128, 185),
    (39, 174, 96),
    (142, 68, 173),
]

banner_texts = [
    "佳木斯大学",
    "设施管理系统",
    "智慧校园"
]

for i, (color, text) in enumerate(zip(banner_colors, banner_texts), 1):
    create_placeholder_image(
        os.path.join(media_dir, 'banner', f'campus{i}.jpg'),
        1200, 400, text, color
    )

equipment_data = [
    ('aircon.jpg', (52, 152, 219), '空调设备'),
    ('computer.jpg', (46, 204, 113), '电脑设备'),
    ('projector.jpg', (155, 89, 182), '投影设备'),
]

for filename, color, text in equipment_data:
    create_placeholder_image(
        os.path.join(media_dir, 'equipment', filename),
        400, 300, text, color
    )

announcement_data = [
    ('notice1.jpg', (230, 126, 34), '系统公告'),
    ('notice2.jpg', (231, 76, 60), '重要通知'),
]

for filename, color, text in announcement_data:
    create_placeholder_image(
        os.path.join(media_dir, 'announcement', filename),
        600, 300, text, color
    )

default_avatar = os.path.join(media_dir, 'avatar', 'default.jpg')
create_placeholder_image(default_avatar, 200, 200, '用户', (149, 165, 166), (255, 255, 255))

print("\n所有占位图片创建完成！")
