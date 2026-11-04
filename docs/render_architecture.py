"""Render the project architecture PNG: python docs/render_architecture.py."""
from pathlib import Path
import math
from PIL import Image, ImageDraw, ImageFont

OUT = Path(__file__).with_name('architecture.png')
img = Image.new('RGB', (2400, 1760), '#f2f5fa')
d = ImageDraw.Draw(img)
fonts = Path('C:/Windows/Fonts')

def font(size, bold=False):
    filename = 'arialbd.ttf' if bold else 'arial.ttf'
    try:
        return ImageFont.truetype(str(fonts / filename), size)
    except OSError:
        return ImageFont.load_default(size=size)

def label(x, y, text, size=27, fill='#193451', bold=False):
    d.multiline_text((x,y), text, font=font(size,bold), fill=fill, spacing=9)

def box(bounds, title, detail='', color='#ffffff', border='#a9bbd1', title_size=29):
    d.rounded_rectangle(bounds, radius=18, fill=color, outline=border, width=3)
    x1,y1,x2,y2 = bounds
    lines = title + ('\n' + detail if detail else '')
    f = font(title_size)
    bbox = d.multiline_textbbox((0,0), lines, font=f, spacing=9, align='center')
    d.multiline_text(((x1+x2)/2-(bbox[2]-bbox[0])/2, (y1+y2)/2-(bbox[3]-bbox[1])/2-5),
                     lines, font=f, spacing=9, align='center', fill='#17324d')

def arrow(points, color='#456a92', dashed=False):
    for a,b in zip(points,points[1:]):
        if dashed:
            length=math.dist(a,b)
            for start in range(0,int(length),22):
                end=min(start+12,length)
                d.line([(a[0]+(b[0]-a[0])*start/length,a[1]+(b[1]-a[1])*start/length),
                        (a[0]+(b[0]-a[0])*end/length,a[1]+(b[1]-a[1])*end/length)],fill=color,width=4)
        else:
            d.line([a,b],fill=color,width=4)
    a,b=points[-2:]
    angle=math.atan2(b[1]-a[1],b[0]-a[0])
    d.polygon([b,(b[0]-18*math.cos(angle-.45),b[1]-18*math.sin(angle-.45)),
               (b[0]-18*math.cos(angle+.45),b[1]-18*math.sin(angle+.45))],fill=color)

label(65,40,'InsightLens | Group 3 architecture',55,bold=True)
label(68,112,'Synthetic business data  /  ingestion, indexing and question answering',29)
# Background panels.
d.rounded_rectangle((50,190,1030,1400),radius=25,fill='#e7eff9')
d.rounded_rectangle((1070,190,2350,1400),radius=25,fill='#e7f3ef')
label(85,220,'01  INGESTION + INDEXING',34,bold=True)
label(1105,220,'02  QUERY + RESPONSE',34,bold=True)
label(85,275,'Separate indexing command; not launched by the UI.',25)
label(1105,275,'RAGPipeline routes supported calculations directly to CSV.',25)

lefts=[85,320,555,790]
inputs=['Report PDF','Chart PNGs','Transcript JSON','Sales CSV']
processors=['PyMuPDF\nPage text','CSV-backed\nChart captions','Python JSON\nText + times','Pandas\nMonthly rows']
for x,title,processor in zip(lefts,inputs,processors):
    box((x,350,x+210,440),title,title_size=25)
    arrow([(x+105,440),(x+105,490)])
    box((x,490,x+210,625),processor,title_size=25)
    arrow([(x+105,625),(x+105,680),(540,680),(540,725)])
label(330,693,'CSV also verifies chart values',22)
box((160,725,920,855),'Standard records: id, text, metadata',
    'Source + modality + PDF page / CSV row / transcript times',title_size=25)
arrow([(540,855),(540,915)])
box((160,915,920,1040),'Sentence Transformers',
    'all-MiniLM-L6-v2  |  document embeddings',color='#d9e7fb')
arrow([(540,1040),(540,1100)])
box((160,1100,920,1245),'Persistent ChromaDB',
    'Collection: insightlens_multimodal\nVectors + text + IDs + source metadata',color='#d9e7fb')
label(165,1280,'Storage: data/processed/chroma_db',26)
label(165,1325,'Chart captions currently use templates + CSV, not vision.',23)

box((1410,340,2010,430),'User question in Streamlit')
arrow([(1710,430),(1710,475)])
box((1410,475,2010,565),'RAGPipeline.ask',color='#d5ece4')
arrow([(1500,565),(1500,620),(1390,620),(1390,670)])
arrow([(1920,565),(1920,620),(2020,620),(2020,670)])
label(1150,580,'Supported numerical question',23)
label(1850,580,'Document question',23)
box((1110,670,1670,810),'DataAnalyzer + sales CSV',
    'Revenue / profit / margins\nExact calculations; INR lakh',title_size=27)
arrow([(1390,810),(1390,1175)])
box((1110,1175,1670,1285),'Numerical answer',
    'CSV source filename',color='#d5ece4')

box((1730,670,2310,810),'Configured Retriever',
    'Same embedding model for query\nChromaDB search: top_k',title_size=27)
arrow([(920,1170),(1050,1170),(1050,865),(1710,865),(1710,740),(1730,740)],dashed=True)
label(1110,900,'Indexed collection\n(configured retrieval)',22)
arrow([(2020,810),(2020,900)])
box((1730,900,2310,1010),'Retrieved context + metadata',
    'No matches: explicit no-information answer',title_size=25)
arrow([(2020,1010),(2020,1060)])
box((1730,1060,2310,1160),'OpenAI Responses API',
    'LLMService: evidence-grounded prompt',title_size=26)
arrow([(2020,1160),(2020,1205)])
box((1730,1205,2310,1310),'Generated answer',
    'Returned with retrieved source metadata',color='#d5ece4',title_size=25)
label(1110,1345,'Responses return to Streamlit with their available sources.',25)

# Actual integration status is explicit, separate from the available module flow.
d.rounded_rectangle((50,1440,2350,1710),radius=24,fill='#fff2dd',outline='#dbb678',width=3)
label(85,1470,'CURRENT APPLICATION STATUS',30,bold=True,fill='#714b16')
label(85,1520,'app.py creates RAGPipeline() without a retriever or LLM. Numerical answers work.',28)
label(85,1565,'Document questions currently show: "Document retrieval is not connected yet."',28)
label(85,1610,'The document flow above requires service wiring. CSV row citations and transcript validation still have gaps.',26)
label(85,1655,'Diagram reflects the existing modules; it does not claim a verified end-to-end document retrieval run.',25)
img.save(OUT)
print(OUT)
