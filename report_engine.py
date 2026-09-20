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
    out=empty_session("TODOS OS TREINOS")
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
    kdata=[["TENTATIVAS","ACERTOS","ERROS","TAXA DE ACERTO","TREINOS"],
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
        story += [PageBreak(),Paragraph("EVOLUCAO ENTRE TREINOS",title)]
        ev=[["TREINO","TENTATIVAS","ACERTOS","ERROS","TAXA","DIFICULDADE ALTA"]]
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
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import A3, landscape
    from reportlab.lib import colors
    from reportlab.lib.units import mm
    from reportlab.lib.utils import ImageReader
    import math

    buf=io.BytesIO(); W,H=landscape(A3)
    bg=colors.HexColor("#06111f"); panel=colors.HexColor("#0b1d31")
    panel2=colors.HexColor("#0d243b"); white=colors.HexColor("#f5f8ff")
    muted=colors.HexColor("#9bb2c8"); blue=colors.HexColor("#1398ff")
    lightblue=colors.HexColor("#6bc1f7"); red=colors.HexColor("#ff4050")
    green=colors.HexColor("#16d98b"); yellow=colors.HexColor("#f4cf43")
    purple=colors.HexColor("#a46cff"); orange=colors.HexColor("#ff8b3d")
    palette=[blue,lightblue,red,green,yellow,purple,orange]
    c=canvas.Canvas(buf,pagesize=(W,H))

    def page_bg():
        c.setFillColor(bg); c.rect(0,0,W,H,fill=1,stroke=0)

    def header(sub="PERFORMANCE ANALYSIS • TRAINING INTELLIGENCE"):
        c.setFillColor(panel); c.roundRect(10*mm,H-31*mm,W-20*mm,20*mm,4*mm,fill=1,stroke=0)
        # Cabeçalho com posições calculadas para nunca sobrepor PERFORMANCE / TIME BRASIL
        hx=17*mm
        c.setFillColor(white); c.setFont("Helvetica-BoldOblique",23)
        c.drawString(hx,H-22*mm,"SKATE")
        skate_w=c.stringWidth("SKATE","Helvetica-BoldOblique",23)

        perf_x=hx+skate_w+2.0*mm
        c.setFillColor(blue); c.setFont("Helvetica-BoldOblique",23)
        c.drawString(perf_x,H-22*mm,"PERFORMANCE")
        perf_w=c.stringWidth("PERFORMANCE","Helvetica-BoldOblique",23)

        time_x=perf_x+perf_w+5.5*mm
        c.setStrokeColor(colors.HexColor("#6f8da5")); c.setLineWidth(.6)
        c.line(time_x-2.8*mm,H-26*mm,time_x-2.8*mm,H-16.5*mm)
        c.setFillColor(white); c.setFont("Helvetica-Bold",11.5)
        c.drawString(time_x,H-22*mm,"TIME BRASIL")
        c.setFillColor(lightblue); c.setFont("Helvetica",8.5); c.drawString(17*mm,H-27*mm,sub)
        c.setFillColor(blue); c.setFont("Helvetica-Bold",9.5); c.drawRightString(W-17*mm,H-21*mm,"SPORTSCODE ANALYTICS")
        c.setFillColor(muted); c.setFont("Helvetica",8); c.drawRightString(W-17*mm,H-26*mm,"TRAINING DATA DASHBOARD")

    def section(title,y):
        c.setFillColor(white); c.setFont("Helvetica-Bold",17); c.drawString(12*mm,y,title)

    def card(x,y,w,h,label,value,sub="",value_color=None):
        c.setFillColor(panel2); c.roundRect(x,y,w,h,3*mm,fill=1,stroke=0)
        c.setStrokeColor(colors.HexColor("#245071")); c.roundRect(x,y,w,h,3*mm,fill=0,stroke=1)
        c.setFillColor(muted); c.setFont("Helvetica-Bold",12.5); c.drawString(x+4*mm,y+h-7*mm,label)
        c.setFillColor(value_color or white); c.setFont("Helvetica-Bold",30); c.drawString(x+4*mm,y+8*mm,str(value))
        if sub:
            c.setFillColor(lightblue if value_color is None else value_color); c.setFont("Helvetica",11.5); c.drawString(x+4*mm,y+3.5*mm,sub)

    def donut(x,y,r,title,data,colorset=None):
        vals=[(str(k),float(v)) for k,v in data.items() if float(v)>0]
        total=sum(v for _,v in vals)
        c.setFillColor(white); c.setFont("Helvetica-Bold",15); c.drawCentredString(x,y+r+9*mm,title)
        if not vals or total<=0:
            c.setFillColor(muted); c.setFont("Helvetica",10); c.drawCentredString(x,y,"SEM DADOS"); return

        # Cores fixas por significado. Assim pizza e legenda sempre usam a MESMA cor,
        # independentemente da ordem em que o Sportscode exportar as categorias.
        semantic = {
            "ACERTO": green, "ERRO": red,
            "BOM": blue, "RUIM": red, "EXCELENTE": green,
            "BAIXA": blue, "MEDIA": green, "MÉDIA": green, "ALTA": red,
            "BAIXO": blue, "MEDIO": green, "MÉDIO": green, "ALTO": red,
            "NORMAL": blue, "LENTO": red, "RAPIDO": green, "RÁPIDO": green,
            "SWITCH": blue, "NOLLIE": green, "FAKIE": red,
            "FRONTSIDE": green, "BACKSIDE": lightblue, "REVERSE": red,
        }
        assigned=[]
        for i,(lab,v) in enumerate(vals):
            key=lab.strip().upper()
            if colorset is not None and i < len(colorset):
                assigned.append(colorset[i])
            elif key in semantic:
                assigned.append(semantic[key])
            else:
                assigned.append(palette[i%len(palette)])

        angle=90
        for i,(lab,v) in enumerate(vals):
            extent=360*v/total
            c.setFillColor(assigned[i])
            c.wedge(x-r,y-r,x+r,y+r,angle,extent,fill=1,stroke=0)
            # V2.0 — percentual diretamente na fatia do dashboard visual.
            # Posiciona o texto entre o furo e a borda para permanecer legível.
            import math
            mid = math.radians(angle + extent / 2.0)
            tx = x + math.cos(mid) * r * .79
            ty = y + math.sin(mid) * r * .79
            pct = v / total * 100
            c.setFillColor(white)
            c.setFont("Helvetica-Bold", 15.5 if extent >= 24 else 12.0)
            c.drawCentredString(tx, ty-1.5, f"{pct:.0f}%")
            angle+=extent
        c.setFillColor(bg); c.circle(x,y,r*.58,fill=1,stroke=0)

        ly=y-r-7*mm; colw=36*mm
        for i,(lab,v) in enumerate(vals[:8]):
            row=i//2; col=i%2; lx=x-r+col*colw
            c.setFillColor(assigned[i]); c.rect(lx,ly-row*5*mm,2.5*mm,2.5*mm,fill=1,stroke=0)
            c.setFillColor(white); c.setFont("Helvetica-Bold",10.8)
            pct=v/total*100
            c.drawString(lx+4*mm,ly-row*5*mm,f"{lab[:16]}  {pct:.1f}%")

    def line_chart(x,y,w,h,title,values,color=blue,suffix=""):
        c.setFillColor(white); c.setFont("Helvetica-Bold",13); c.drawString(x,y+h+5*mm,title)
        c.setStrokeColor(colors.HexColor("#173047")); c.setLineWidth(.5)
        for j in range(5):
            gy=y+j*h/4; c.line(x,gy,x+w,gy)
        if not values:return
        mx=max(max(values),1); pts=[]
        for i,v in enumerate(values):
            xx=x+w*(i/max(1,len(values)-1)); yy=y+h*(v/mx*.88); pts.append((xx,yy))
        c.setStrokeColor(color); c.setLineWidth(2)
        for a,b in zip(pts,pts[1:]): c.line(a[0],a[1],b[0],b[1])
        for i,(xx,yy) in enumerate(pts):
            c.setFillColor(color); c.circle(xx,yy,1.7*mm,fill=1,stroke=0)
            c.setFillColor(white); c.setFont("Helvetica-Bold",8); c.drawCentredString(xx,yy+3*mm,f"{values[i]:.1f}{suffix}")
            c.setFillColor(muted); c.setFont("Helvetica",7); c.drawCentredString(xx,y-4*mm,sessions[i]["name"][:24])

    # PAGE 1
    page_bg(); header()
    # Athlete/photo block
    px,py,pw,ph=12*mm,H-92*mm,55*mm,54*mm
    c.setFillColor(panel); c.roundRect(px,py,pw,ph,3*mm,fill=1,stroke=0)
    if photo_file is not None:
        try:
            photo_file.seek(0); im=ImageReader(photo_file)
            iw,ih=im.getSize(); scale=min((pw-4*mm)/iw,(ph-4*mm)/ih)
            dw,dh=iw*scale,ih*scale
            c.drawImage(im,px+(pw-dw)/2,py+(ph-dh)/2,dw,dh,preserveAspectRatio=True,mask='auto')
        except Exception: pass
    c.setFillColor(white); c.setFont("Helvetica-Bold",22); c.drawString(12*mm,H-101*mm,(athlete or "ATLETA").upper())
    c.setFillColor(muted); c.setFont("Helvetica",12); c.drawString(12*mm,H-107*mm,f"{len(sessions)} treino(s) • {choice}")

    rate=cur["hits"]/cur["attempts"]*100 if cur["attempts"] else 0
    vals=[("TENTATIVAS",f'{cur["attempts"]:.0f}',"volume total",None),
          ("MANOBRAS",str(len(cur["maneuvers"])),"diferentes",None),
          ("ACERTOS",f'{cur["hits"]:.0f}',f"{rate:.1f}% de acerto",None),
          ("ERROS",f'{cur["errors"]:.0f}',f"{100-rate:.1f}%",red),
          ("TREINOS",str(len(sessions)),"CSVs importados",None)]
    kx=73*mm; ky=H-78*mm; gap=3*mm; kw=(W-kx-12*mm-gap*4)/5
    for i,(lab,val,sub,col) in enumerate(vals): card(kx+i*(kw+gap),ky,kw,28*mm,lab,val,sub,col)

    section("DISTRIBUIÇÕES GERAIS",H-123*mm)
    cy=H-169*mm; rr=25*mm
    ds=[("RESULTADO",{"ACERTO":cur["hits"],"ERRO":cur["errors"]},[green,red]),
        ("DIFICULDADE",cur["cats"]["DIFICULDADE"],None),
        ("RISCO",cur["cats"]["RISCO"],None),
        ("DIREÇÃO",cur["cats"]["DIRECAO"],None)]
    centers=[58*mm,150*mm,242*mm,334*mm]
    for xx,(t,d,cc) in zip(centers,ds): donut(xx,cy,rr,t,d,cc)

    # Maneuver table lower
    section("MANOBRAS",H-221*mm)
    tx=12*mm; ty=H-232*mm; widths=[12*mm,220*mm,38*mm,38*mm,38*mm,44*mm]
    headers=["#","MANOBRA","ACERTOS","ERROS","TOTAL","TAXA"]
    c.setFillColor(colors.HexColor("#0d2237")); c.rect(tx,ty-8*mm,sum(widths),8*mm,fill=1,stroke=0)
    c.setFillColor(muted); c.setFont("Helvetica-Bold",10.5); xx=tx
    for h,w in zip(headers,widths): c.drawString(xx+2*mm,ty-5*mm,h); xx+=w
    yy=ty-15*mm
    all_maneuvers=sorted(cur["maneuvers"].items(),key=lambda z:sum(z[1]),reverse=True)
    for idx,(m,(hh,ee)) in enumerate(all_maneuvers[:8],1):
        tt=hh+ee; rr2=hh/tt*100 if tt else 0
        row=[str(idx),m[:35],f"{hh:.0f}",f"{ee:.0f}",f"{tt:.0f}",f"{rr2:.1f}%"]
        c.setFillColor(panel if idx%2 else panel2); c.rect(tx,yy,sum(widths),6.7*mm,fill=1,stroke=0)
        xx=tx
        for j,(v,w) in enumerate(zip(row,widths)):
            c.setFillColor(red if j==3 else (blue if j in (2,5) else white)); c.setFont("Helvetica-Bold" if j in (1,2,3,5) else "Helvetica",11.5)
            c.drawString(xx+2*mm,yy+2.2*mm,v); xx+=w
        yy-=7.2*mm
    c.showPage()

    # PÁGINAS EXTRAS: todas as manobras restantes, sem cortar a lista.
    remaining=all_maneuvers[8:]
    chunk_size=28
    for chunk_start in range(0,len(remaining),chunk_size):
        page_bg(); header("MANEUVER ANALYSIS • COMPLETE LIST")
        section("MANOBRAS — CONTINUAÇÃO",H-45*mm)
        tx=12*mm; ty=H-57*mm
        widths=[12*mm,220*mm,38*mm,38*mm,38*mm,44*mm]
        headers=["#","MANOBRA","ACERTOS","ERROS","TOTAL","TAXA"]
        c.setFillColor(colors.HexColor("#0d2237")); c.rect(tx,ty-9*mm,sum(widths),9*mm,fill=1,stroke=0)
        c.setFillColor(muted); c.setFont("Helvetica-Bold",10.5); xx=tx
        for h,w in zip(headers,widths):
            c.drawString(xx+2*mm,ty-5.8*mm,h); xx+=w
        yy=ty-17*mm
        chunk=remaining[chunk_start:chunk_start+chunk_size]
        for local_i,(m,(hh,ee)) in enumerate(chunk):
            idx=9+chunk_start+local_i
            tt=hh+ee; rr2=hh/tt*100 if tt else 0
            row=[str(idx),m[:58],f"{hh:.0f}",f"{ee:.0f}",f"{tt:.0f}",f"{rr2:.1f}%"]
            c.setFillColor(panel if idx%2 else panel2); c.rect(tx,yy,sum(widths),7*mm,fill=1,stroke=0)
            xx=tx
            for j,(v,w) in enumerate(zip(row,widths)):
                c.setFillColor(red if j==3 else (blue if j in (2,5) else white))
                c.setFont("Helvetica-Bold" if j in (1,2,3,5) else "Helvetica",11.5)
                c.drawString(xx+2*mm,yy+2.3*mm,v); xx+=w
            yy-=7.6*mm
        c.setFillColor(muted); c.setFont("Helvetica",8)
        c.drawRightString(W-12*mm,10*mm,f"Manobras {9+chunk_start}–{8+chunk_start+len(chunk)} de {len(all_maneuvers)}")
        c.showPage()

    # ÚLTIMA PÁGINA: evolution + details
    page_bg(); header("SESSION EVOLUTION • PERFORMANCE DISTRIBUTION")
    section("EVOLUÇÃO ENTRE TREINOS",H-45*mm)
    rates=[ss["hits"]/ss["attempts"]*100 if ss["attempts"] else 0 for ss in sessions]
    line_chart(18*mm,H-105*mm,W-36*mm,45*mm,"TAXA DE ACERTO",rates,blue,"%")
    section("EVOLUÇÃO DA DIFICULDADE",H-125*mm)
    chartw=(W-42*mm)/3
    for i,(dif,col) in enumerate([("ALTA",red),("MEDIA",blue),("BAIXA",lightblue)]):
        vv=[ss["cats"]["DIFICULDADE"].get(dif,0) for ss in sessions]
        line_chart(14*mm+i*(chartw+7*mm),H-180*mm,chartw,35*mm,dif,vv,col,"")
    section("DETALHES",H-201*mm)
    details=[("AVALIAÇÃO",cur["cats"]["AVALIACAO"]),("VELOCIDADE",cur["cats"]["VELOCIDADE"]),
             ("OBSTÁCULO",cur["cats"]["OBSTACULO"]),("BASE",cur["cats"]["BASE"])]
    for xx,(t,d) in zip(centers,details): donut(xx,H-246*mm,22*mm,t,d,None)
    c.save(); buf.seek(0); return buf.getvalue()
