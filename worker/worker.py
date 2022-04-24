import pika
import json

from fpdf import FPDF
import requests
from io import BytesIO

connection = pika.BlockingConnection(pika.ConnectionParameters('rabbitmq'))
channel = connection.channel()

channel.queue_declare(queue='queue', durable=True)


def callback(ch, method, properties, body):
    d = json.loads(body.decode())
    user_id = d['id']
    image = requests.get(d['avatar_url']).content
    image_path = f'/data/images/{user_id}.jpg'
    with open(image_path, 'wb') as f:
        f.write(image)
    pdf_path = f'/data/reports/{user_id}'
    pdf = FPDF('P', 'mm', 'A4')
    pdf.add_page()
    pdf.set_margins(0, 0, 0)
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(w=40, h=10, txt=f"name: {d['name']}", border=0, ln=1, align='', fill=False, link='')
    pdf.cell(w=40, h=10, txt=f"gender: {d['gender']}", border=0, ln=1, align='', fill=False, link='')
    pdf.cell(w=40, h=10, txt=f"email: {d['email']}", border=0, ln=1, align='', fill=False, link='')
    pdf.image(image_path, x=85, y=32.5, w=40, h=0, type='', link='')
    pdf.cell(w=40, h=10, txt="sessions: 432412", border=0, ln=1, align='', fill=False, link='')
    pdf.cell(w=40, h=10, txt="win: 32412", border=0, ln=1, align='', fill=False, link='')
    pdf.cell(w=40, h=10, txt="lose: 400000", border=0, ln=1, align='', fill=False, link='')
    pdf.cell(w=40, h=10, txt="hours in game: 342412", border=0, ln=1, align='', fill=False, link='')
    pdf.output(pdf_path, 'F')
    ch.basic_ack(delivery_tag=method.delivery_tag)


channel.basic_consume(queue='queue', on_message_callback=callback)
channel.start_consuming()
