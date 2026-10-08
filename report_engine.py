import io, re, unicodedata
import pandas as pd

def norm(s):
    s=unicodedata.normalize("NFKD",str(s)).encode("ascii","ignore").decode()
    return re.sub(r"\s+"," ",s.strip()).upper()

def read_csv(f):
    raw=f.getvalue()
    for enc in ("utf-8-sig","utf-8","latin1"):
        for sep in (None,",",";","\t"):
            try:
                kw={"encoding":enc}
                if sep is None: kw.update(sep=None,engine="python")
                else: kw["sep"]=sep
                d=pd.read_csv(io.BytesIO(raw),**kw)
                if len(d.columns)>1:return d
            except: pass
    raise ValueError("Formato CSV não reconhecido")

def is_aggregate(d):
    return any(":" in str(c) for c in d.columns)

def empty_session(name):
    return {"name":name,"attempts":0,"hits":0,"errors":0,"maneuvers":{},
            "cats":{k:{} for k in ["AVALIACAO","DIFICULDADE","RISCO","DIRECAO","VELOCIDADE","OBSTACULO","BASE"]}}

def add(dic,key,n=1):
    key=norm(key)
    if key and key not in ("NAN","0","NONE"):
        dic[key]=dic.get(key,0)+float(n)

def parse_raw(d,name):
    d=d.copy(); d.columns=[norm(c) for c in d.columns]
    s=empty_session(name)
    # Sportscode raw export: Row = maneuver, ACERTOS = result
    mcol="ROW" if "ROW" in d.columns else next((c for c in ["MANOBRA","TRICK","CODE"] if c in d.columns),None)
    for _,r in d.iterrows():
        result=norm(r.get("ACERTOS",""))
        valid=result in ("ACERTO","ERRO")
        if valid:
            s["attempts"]+=1
            s["hits"]+=result=="ACERTO"; s["errors"]+=result=="ERRO"
            man=norm(r.get(mcol,"")) if mcol else ""
            if man and man!="NAN":
                if man not in s["maneuvers"]:s["maneuvers"][man]=[0,0]
                s["maneuvers"][man][0 if result=="ACERTO" else 1]+=1
        # categories can exist even on rows without result; count only valid attempts for consistency
        if valid:
            for cat in s["cats"]:
                val=r.get(cat,"")
                if pd.isna(val):continue
                # direction may contain "FRONTSIDE, REVERSE"
                vals=[v.strip() for v in str(val).split(",")]
                for v in vals:add(s["cats"][cat],v)
    return s

def parse_aggregate(d,name):
    d=d.copy(); d.columns=[norm(c) for c in d.columns]
    s=empty_session(name)
    mcol=d.columns[0]
    # first column is maneuver name in pivoted Sportscode CSV
    for _,r in d.iterrows():
        h=float(pd.to_numeric(r.get("ACERTOS:ACERTO",0),errors="coerce") or 0)
        e=float(pd.to_numeric(r.get("ACERTOS:ERRO",0),errors="coerce") or 0)
        man=norm(r.get(mcol,""))
        if h+e>0 and man not in ("","NAN","0"):
            s["maneuvers"][man]=[h,e]
        s["hits"]+=h;s["errors"]+=e
        for cat in s["cats"]:
            pref=cat+":"
            for c in d.columns:
                if c.startswith(pref):
                    v=pd.to_numeric(r.get(c,0),errors="coerce")
                    if pd.notna(v) and float(v)!=0:add(s["cats"][cat],c.split(":",1)[1],float(v))
    s["attempts"]=s["hits"]+s["errors"]
    return s

def merge_sessions(ss):
    out=empty_session("TODAS AS SESSÕES")
    for s in ss:
        for k in ("attempts","hits","errors"):out[k]+=s[k]
        for m,(h,e) in s["maneuvers"].items():
            if m not in out["maneuvers"]:out["maneuvers"][m]=[0,0]
            out["maneuvers"][m][0]+=h;out["maneuvers"][m][1]+=e
        for cat in out["cats"]:
            for k,v in s["cats"][cat].items():add(out["cats"][cat],k,v)
    return out

def make_pdf(athlete, cur, sessions, choice):
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4, landscape
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.enums import TA_LEFT
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
    from reportlab.lib.units import mm

    buf=io.BytesIO()
    doc=SimpleDocTemplate(buf,pagesize=landscape(A4),rightMargin=12*mm,leftMargin=12*mm,topMargin=12*mm,bottomMargin=12*mm)
    styles=getSampleStyleSheet()
    title=ParagraphStyle("T",parent=styles["Title"],fontName="Helvetica-Bold",fontSize=32,textColor=colors.HexColor("#0D4E7A"),alignment=TA_LEFT,spaceAfter=5)
    h=ParagraphStyle("H",parent=styles["Heading2"],fontName="Helvetica-Bold",fontSize=20,textColor=colors.HexColor("#0D4E7A"),spaceBefore=8,spaceAfter=6)
    body=ParagraphStyle("B",parent=styles["BodyText"],fontSize=13,textColor=colors.HexColor("#263746"))
    story=[Paragraph("SKATE PERFORMANCE",title),
           Paragraph(f"{athlete or 'ATLETA'} - {choice}",body),Spacer(1,6)]
    rate=cur["hits"]/cur["attempts"]*100 if cur["attempts"] else 0
    kdata=[["TENTATIVAS","ACERTOS","ERROS","TAXA DE ACERTO","SESSÕES"],
           [f'{cur["attempts"]:.0f}',f'{cur["hits"]:.0f}',f'{cur["errors"]:.0f}',f'{rate:.1f}%',str(len(sessions))]]
    kt=Table(kdata,colWidths=[50*mm]*5,rowHeights=[8*mm,13*mm])
    kt.setStyle(TableStyle([
        ("BACKGROUND",(0,0),(-1,0),colors.HexColor("#0D4E7A")),("TEXTCOLOR",(0,0),(-1,0),colors.white),
        ("BACKGROUND",(0,1),(-1,1),colors.HexColor("#EDF5FA")),("TEXTCOLOR",(0,1),(-1,1),colors.HexColor("#102536")),
        ("FONTNAME",(0,0),(-1,-1),"Helvetica-Bold"),("FONTSIZE",(0,0),(-1,0),10),("FONTSIZE",(0,1),(-1,1),20),
        ("ALIGN",(0,0),(-1,-1),"CENTER"),("VALIGN",(0,0),(-1,-1),"MIDDLE"),
        ("GRID",(0,0),(-1,-1),0.5,colors.HexColor("#A9C7DA"))
    ]))
    story += [kt,Spacer(1,8),Paragraph("MANOBRAS",h)]
    rows=[["MANOBRA","ACERTOS","ERROS","TOTAL","TAXA"]]
    for m,(hh,ee) in sorted(cur["maneuvers"].items(),key=lambda x:sum(x[1]),reverse=True):
        tt=hh+ee; rr=hh/tt*100 if tt else 0
        rows.append([m,f"{hh:.0f}",f"{ee:.0f}",f"{tt:.0f}",f"{rr:.1f}%"])
    if len(rows)==1: rows.append(["Sem dados","0","0","0","0.0%"])
    mt=Table(rows,colWidths=[110*mm,32*mm,32*mm,32*mm,35*mm],repeatRows=1)
    mt.setStyle(TableStyle([
        ("BACKGROUND",(0,0),(-1,0),colors.HexColor("#102C43")),("TEXTCOLOR",(0,0),(-1,0),colors.white),
        ("ROWBACKGROUNDS",(0,1),(-1,-1),[colors.white,colors.HexColor("#F4F8FB")]),
        ("TEXTCOLOR",(0,1),(-1,-1),colors.HexColor("#1D2D3A")),("FONTNAME",(0,0),(-1,0),"Helvetica-Bold"),
        ("FONTSIZE",(0,0),(-1,-1),10),("GRID",(0,0),(-1,-1),0.35,colors.HexColor("#C9D9E4")),
        ("ALIGN",(1,1),(-1,-1),"CENTER"),("VALIGN",(0,0),(-1,-1),"MIDDLE")
    ]))
    story.append(mt)
    if len(sessions)>1:
        story += [PageBreak(),Paragraph("EVOLUCAO ENTRE SESSÕES",title)]
        ev=[["SESSÃO","TENTATIVAS","ACERTOS","ERROS","TAXA","DIFICULDADE ALTA"]]
        for s in sessions:
            rr=s["hits"]/s["attempts"]*100 if s["attempts"] else 0
            alta=s["cats"]["DIFICULDADE"].get("ALTA",0)
            ev.append([s["name"],f'{s["attempts"]:.0f}',f'{s["hits"]:.0f}',f'{s["errors"]:.0f}',f"{rr:.1f}%",f"{alta:.0f}"])
        et=Table(ev,colWidths=[105*mm,30*mm,30*mm,30*mm,30*mm,40*mm],repeatRows=1)
        et.setStyle(TableStyle([
            ("BACKGROUND",(0,0),(-1,0),colors.HexColor("#102C43")),("TEXTCOLOR",(0,0),(-1,0),colors.white),
            ("ROWBACKGROUNDS",(0,1),(-1,-1),[colors.white,colors.HexColor("#F4F8FB")]),
            ("GRID",(0,0),(-1,-1),0.35,colors.HexColor("#C9D9E4")),("FONTSIZE",(0,0),(-1,-1),10),
            ("FONTNAME",(0,0),(-1,0),"Helvetica-Bold"),("ALIGN",(1,1),(-1,-1),"CENTER")
        ]))
        story.append(et)
    doc.build(story)
    buf.seek(0)
    return buf.getvalue()

def make_visual_pdf(athlete, cur, sessions, choice, photo_file=None):
    """Portrait PDF with readable type and space-based pagination (shared by both pages)."""
    from reportlab.pdfgen import canvas
    from reportlab.lib import colors
    from reportlab.lib.utils import ImageReader
    from reportlab.platypus import Paragraph
    from reportlab.lib.styles import ParagraphStyle
    from xml.sax.saxutils import escape
    import math

    W, H, margin = 420, 746, 18
    width = W - 2 * margin
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=(W, H))
    c.setTitle(f'Dashboard - {athlete or "ATLETA"}')
    bg, panel = '#06111f', '#0d243b'
    white, muted, blue, green, red = '#f5f8ff', '#a9c2d8', '#1398ff', '#16d98b', '#ff4050'
    palette = [blue, '#6bc1f7', '#ff8b3d', '#a46cff', '#f4cf43', green, red]
    semantic = {'ACERTO':green, 'ERRO':red, 'EXCELENTE':green, 'BOM':blue, 'RUIM':red,
                'MEDIA':green, 'MEDIO':green, 'BAIXA':blue, 'BAIXO':blue, 'ALTA':red, 'ALTO':red,
                'RAPIDO':green, 'LENTO':red, 'FRONTSIDE':green, 'BACKSIDE':'#6bc1f7', 'NOLLIE':green}
    page, top, legend_step = 0, 0, 36

    def text(x, y, value, size=14, color=white, bold=False):
        c.setFillColor(colors.HexColor(color))
        c.setFont('Helvetica-Bold' if bold else 'Helvetica', size)
        c.drawString(x, y, str(value))

    def wrapped(value, x, y, w, size=14, color=white, bold=False):
        style = ParagraphStyle('mobile', fontName='Helvetica-Bold' if bold else 'Helvetica',
                               fontSize=size, leading=size*1.25, textColor=colors.HexColor(color))
        p = Paragraph(escape(str(value)), style)
        _, h = p.wrap(w, H)
        p.drawOn(c, x, y-h)
        return h

    def new_page():
        nonlocal page, top
        if page: c.showPage()
        page += 1
        c.setFillColor(colors.HexColor(bg)); c.rect(0,0,W,H,fill=1,stroke=0)
        c.setFillColor(colors.HexColor(panel)); c.roundRect(margin,H-66,width,48,8,fill=1,stroke=0)
        text(margin+12,H-39,'SELEÇÃO BRASILEIRA',17,bold=True)
        text(margin+12,H-56,'DE SKATEBOARDING  |  DASHBOARD',11,muted)
        text(margin,14,f'{athlete or "ATLETA"}  •  {page}',10,muted)
        top = H - 86

    def reserve(height):
        if top - height < 38: new_page()

    def heading(title):
        nonlocal top
        text(margin,top-17,title,17,bold=True); top -= 35

    new_page()
    name_x = margin
    if photo_file is not None:
        try:
            photo_file.seek(0)
            c.drawImage(ImageReader(photo_file),margin,top-74,64,74,preserveAspectRatio=True,anchor='c',mask='auto')
            name_x += 76
        except Exception: pass
    wrapped((athlete or 'ATLETA').upper(),name_x,top,width-(name_x-margin),21,bold=True)
    wrapped(f'{len(sessions)} sessões • {choice}',name_x,top-45,width-(name_x-margin),12,muted)
    top -= 90
    rate = cur['hits']/cur['attempts']*100 if cur['attempts'] else 0
    metrics = [('TENTATIVAS',cur['attempts']),('MANOBRAS',len(cur['maneuvers'])),
               ('ACERTOS',cur['hits']),('ERROS',cur['errors']),('SESSÕES',len(sessions)),('TAXA DE ACERTO',f'{rate:.1f}%')]
    cw = (width-12)/2
    for i,(label,value) in enumerate(metrics):
        x = margin+(i%2)*(cw+12); y = top-66-(i//2)*78
        c.setFillColor(colors.HexColor(panel)); c.roundRect(x,y,cw,66,8,fill=1,stroke=0)
        text(x+12,y+45,label,12,muted,True)
        text(x+12,y+14,f'{value:.0f}' if isinstance(value,(int,float)) else value,27,red if label=='ERROS' else green if label in ('ACERTOS','TAXA DE ACERTO') else white,True)
    top -= 238

    def draw_donut(x, y, w, h, title, data, legend_values):
        c.setFillColor(colors.HexColor(panel)); c.roundRect(x,y-h,w,h,8,fill=1,stroke=0)
        text(x+12,y-25,title,14,bold=True)
        vals = [(str(k),float(v)) for k,v in data.items() if float(v)>0]
        total = sum(v for _,v in vals)
        cx,cy,r = x+w/2,y-88,42
        if not total:
            text(x+12,y-79,'Sem dados',14,muted); return
        angle = 90
        for i,(lab,v) in enumerate(vals):
            color = semantic.get(norm(lab),palette[i%len(palette)])
            extent = 360*v/total
            c.setFillColor(colors.HexColor(color)); c.wedge(cx-r,cy-r,cx+r,cy+r,angle,extent,fill=1,stroke=0)
            if v/total>=.08:
                theta = math.radians(angle+extent/2)
                c.setFillColor(colors.HexColor(white)); c.setFont('Helvetica-Bold',12)
                c.drawCentredString(cx+math.cos(theta)*r*.79,cy+math.sin(theta)*r*.79-4,f'{v/total*100:.0f}%')
            angle += extent
        c.setFillColor(colors.HexColor(panel)); c.circle(cx,cy,r*.57,fill=1,stroke=0)
        for i,(lab,v) in legend_values:
            yy = y-151-legend_values.index((i,(lab,v)))*legend_step
            color = semantic.get(norm(lab),palette[i%len(palette)])
            c.setFillColor(colors.HexColor(color)); c.rect(x+12,yy-2,6,6,fill=1,stroke=0)
            wrapped(lab,x+23,yy+8,w-83,11.5,bold=True)
            c.setFillColor(colors.HexColor(white)); c.setFont('Helvetica-Bold',12)
            c.drawRightString(x+w-10,yy,f'{v/total*100:.1f}%')

    def donut_group(title, items):
        nonlocal top, legend_step
        legend_step = 24
        expanded = []
        for label, data in items:
            vals = [(str(k),float(v)) for k,v in data.items() if float(v)>0]
            indexed = list(enumerate(vals))
            for start in range(0,max(1,len(indexed)),8):
                expanded.append((label + (' (cont.)' if start else ''), data, indexed[start:start+8]))
        for i in range(0,len(expanded),2):
            pair = expanded[i:i+2]
            count = max([len(legend) for _,_,legend in pair]+[1])
            legend_style = ParagraphStyle("legend",fontName="Helvetica-Bold",fontSize=11.5,leading=14.375)
            legend_step = 24
            for _,_,legend in pair:
                for _,(label,_) in legend:
                    pp = Paragraph(escape(label),legend_style)
                    _,lh = pp.wrap(cw-83,H)
                    legend_step = max(legend_step,lh+8)
            height = max(174,158+count*legend_step)
            reserve(height+35)
            heading(title if i==0 else title+' - CONTINUAÇÃO')
            for j,(label,data,legend) in enumerate(pair): draw_donut(margin+j*(cw+12),top,cw,height,label,data,legend)
            top -= height+16

    donut_group('DISTRIBUIÇÕES GERAIS',[
        ('RESULTADO',{'ACERTO':cur['hits'],'ERRO':cur['errors']}),
        ('DIFICULDADE',cur['cats']['DIFICULDADE']),('RISCO',cur['cats']['RISCO']),('DIREÇÃO',cur['cats']['DIRECAO'])])

    # The whole table stays together when it fits a page; long tables repeat headers.
    mans = sorted(cur['maneuvers'].items(),key=lambda z:sum(z[1]),reverse=True)
    rows = []
    for idx,(name,(hits,errors)) in enumerate(mans,1):
        style=ParagraphStyle('row',fontName='Helvetica-Bold',fontSize=12.5,leading=15.5,textColor=colors.HexColor(white))
        p=Paragraph(escape(name),style); _,ph=p.wrap(143,H)
        rows.append((idx,p,max(26,ph+10),hits,errors))
    total_height = 70+sum(row[2] for row in rows)
    if total_height <= H-124: reserve(total_height)
    elif top < 150: new_page()
    def table_header(continued=False):
        nonlocal top
        heading('MANOBRAS'+(' - CONTINUAÇÃO' if continued else ''))
        text(margin,top-12,'Manobra',12,muted,True)
        for x,label in [(224,'Ac.'),(269,'Er.'),(314,'Total'),(397,'Taxa')]:
            c.setFillColor(colors.HexColor(muted)); c.setFont('Helvetica-Bold',12); c.drawRightString(x,top-12,label)
        top -= 26
    table_header()
    if not rows:
        text(margin,top-18,'Sem manobras registradas',14,muted); top -= 40
    for idx,p,rh,hits,errors in rows:
        if top-rh<38: new_page(); table_header(True)
        c.setFillColor(colors.HexColor(panel if idx%2 else '#102b44')); c.rect(margin,top-rh,width,rh-2,fill=1,stroke=0)
        text(margin+5,top-20,idx,11,muted)
        _,ph=p.wrap(143,H); p.drawOn(c,margin+27,top-8-ph)
        total=hits+errors
        for x,value,col in [(224,f'{hits:.0f}',blue),(269,f'{errors:.0f}',red),(314,f'{total:.0f}',white),(397,f'{hits/total*100 if total else 0:.1f}%',green)]:
            c.setFillColor(colors.HexColor(col)); c.setFont('Helvetica-Bold',13); c.drawRightString(x,top-rh/2-4,value)
        top -= rh
    top -= 20
    donut_group('DETALHES',[(label,cur['cats'][key]) for label,key in [('AVALIAÇÃO','AVALIACAO'),('VELOCIDADE','VELOCIDADE'),('OBSTÁCULO','OBSTACULO'),('BASE','BASE')]])

    # Eight sessions per panel keeps values and labels readable for long histories.
    for start in range(0,len(sessions),8):
        group=sessions[start:start+8]
        for label,key,color in [('TAXA DE ACERTO',None,blue),('DIFICULDADE ALTA','ALTA',red),('DIFICULDADE MÉDIA','MEDIA',green),('DIFICULDADE BAIXA','BAIXA','#6bc1f7')]:
            reserve(185); heading(label)
            x,y,w,h=margin+12,top-110,width-24,100
            c.setStrokeColor(colors.HexColor('#244058')); c.setLineWidth(.5)
            for j in range(5): c.line(x,y+j*h/4,x+w,y+j*h/4)
            values=[s['hits']/s['attempts']*100 if s['attempts'] else 0 for s in group] if key is None else [sum(float(v) for k,v in s['cats']['DIFICULDADE'].items() if norm(k)==key) for s in group]
            maximum=100 if key is None else max(max(values,default=0),1)
            points=[(x+w*(i/max(1,len(group)-1)),y+h*.82*v/maximum) for i,v in enumerate(values)]
            c.setStrokeColor(colors.HexColor(color)); c.setLineWidth(2)
            for a,b in zip(points,points[1:]): c.line(*a,*b)
            for i,(xx,yy) in enumerate(points):
                c.setFillColor(colors.HexColor(color)); c.circle(xx,yy,3,fill=1,stroke=0)
                c.setFillColor(colors.HexColor(white)); c.setFont('Helvetica-Bold',12)
                c.drawCentredString(xx,yy+10,f'{values[i]:.1f}%' if key is None else f'{values[i]:g}')
                c.setFillColor(colors.HexColor(muted)); c.setFont('Helvetica',11); c.drawCentredString(xx,y-19,str(start+i+1))
            text(margin,top-152,'Sessões (ordem do histórico)',11,muted); top -= 173
        reserve(25+24*len(group)); heading('IDENTIFICAÇÃO DOS SESSÕES')
        for i,s in enumerate(group):
            reserve(42); hh=wrapped(f'{start+i+1}. {s["name"]}',margin,top,width,13); top -= hh+10
    c.save(); return buf.getvalue()
