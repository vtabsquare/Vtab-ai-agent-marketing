import hashlib
import html
import json
import re


class CheckFailure(ValueError):
    pass


def content_hash(c):
    artifacts = {k: c["results"][k] for k in ("writing", "creative")}
    return hashlib.sha256(json.dumps(artifacts, sort_keys=True, ensure_ascii=True).encode()).hexdigest()


def validate_copy(output, brand):
    # Protect factual price fields; semantic brand review handles creative language.
    normalize = lambda value: re.sub(r"[\s,]", "", value).casefold()
    brand_price_match = re.search(r"(?:INR|USD|EUR|GBP|Rs\.?|₹|\$|€|£)\s*[\d,]+(?:\.\d+)?", brand['price'], re.I)
    expected_price = normalize(brand_price_match.group(0)) if brand_price_match else normalize(brand['price'])

    output_price_match = re.search(r"(?:INR|USD|EUR|GBP|Rs\.?|₹|\$|€|£)\s*[\d,]+(?:\.\d+)?", output.get('price_claim', ''), re.I)
    actual_price = normalize(output_price_match.group(0)) if output_price_match else normalize(output.get('price_claim', ''))

    is_free = lambda p: p in {'freetojoin', 'free', '0', '$0', 'inr0', 'rs0', 'rs.0', '\u20b90', 'freecost', 'nocost', 'complimentary'} or 'free' in p or 'no cost' in p or 'no fee' in p

    # When the brand price is free, there's no specific currency amount to enforce.
    # Only check that the copy's price_claim is also free-tier; skip currency enforcement in caption/variants.
    brand_is_free = is_free(expected_price)

    if brand_is_free:
        # Accept any free-phrased price_claim; reject explicit non-free currency amounts
        if actual_price and not is_free(actual_price) and brand_price_match is None:
            raise CheckFailure('The price conflicts with the approved brand price.')
    else:
        if actual_price != expected_price:
            raise CheckFailure('The price conflicts with the approved brand price.')

    if not brand_is_free:
        # Only enforce caption currency when the brand has a specific paid price
        for claim in re.findall(r"(?:INR|USD|EUR|GBP|Rs\.?|₹|\$|€|£)\s*[\d,]+(?:\.\d+)?", output['caption'], re.I):
            c_norm = normalize(claim)
            if c_norm != expected_price:
                raise CheckFailure('The caption contains an unapproved price.')

        for variant in output.get('variants', []):
            for claim in re.findall(r"(?:INR|USD|EUR|GBP|Rs\.?|₹|\$|€|£)\s*[\d,]+(?:\.\d+)?", variant.get('body', ''), re.I):
                c_norm = normalize(claim)
                if c_norm != expected_price:
                    raise CheckFailure('A channel variant contains an unapproved price.')


def brand_card(c):
    import textwrap
    b=c['snapshot']['brand']
    creative=c.get('results',{}).get('creative',{}).get('output',{})
    writing=c.get('results',{}).get('writing',{}).get('output',{})
    primary=creative.get('primary_hex','#172554')
    accent=creative.get('accent_hex','#38bdf8')
    if not re.fullmatch(r'#[0-9a-fA-F]{6}',primary): primary='#172554'
    if not re.fullmatch(r'#[0-9a-fA-F]{6}',accent): accent='#38bdf8'
    title=creative.get('headline',writing.get('headline','Your next chapter'))
    name=html.escape(b['name'].upper()); price=html.escape(b['price'])
    layout=creative.get('layout_style','split')
    image=c.get('results',{}).get('creative',{}).get('image')
    def lines(text,x,y,width,size,max_lines=4,center=False):
        # Fit complete text and long words without overflowing the canvas.
        while True:
            wrapped=textwrap.wrap(text,width=max(8,int(width/(size*.62)))) or ['']
            if len(wrapped)<=max_lines or size<=18: break
            size-=2
        anchor='middle' if center else 'start'
        return ''.join(f'<text x="{x}" y="{y+i*size*1.18}" fill="#ffffff" font-size="{size}" font-weight="700" text-anchor="{anchor}">{html.escape(line)}</text>' for i,line in enumerate(wrapped))
    def art(x,y,w,h):
        clip=f'<clipPath id="art"><rect x="{x}" y="{y}" width="{w}" height="{h}" rx="28"/></clipPath>'
        if image:
            return clip+f'<image href="{image}" x="{x}" y="{y}" width="{w}" height="{h}" preserveAspectRatio="xMidYMid slice" clip-path="url(#art)"/>'
        return clip+f'<g clip-path="url(#art)"><rect x="{x}" y="{y}" width="{w}" height="{h}" fill="url(#glow)"/><circle cx="{x+w*.65}" cy="{y+h*.42}" r="{w*.39}" fill="none" stroke="{accent}" stroke-opacity=".45" stroke-width="{w*.12}"/><circle cx="{x+w*.25}" cy="{y+h*.75}" r="{w*.3}" fill="{accent}" fill-opacity=".18"/><path d="M{x} {y+h*.65} L{x+w} {y+h*.3} L{x+w} {y+h} L{x} {y+h} Z" fill="{primary}" fill-opacity=".45"/></g>'
    svg=f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1080 1080" role="img"><title>{html.escape(title)}</title><defs><linearGradient id="glow" x2="1" y2="1"><stop stop-color="{primary}"/><stop offset="1" stop-color="{accent}" stop-opacity=".45"/></linearGradient></defs><rect width="1080" height="1080" fill="{primary}"/><g font-family="Arial, sans-serif">'
    if layout=='full-bleed':
        svg+=art(0,0,1080,1080)+'<rect width="1080" height="1080" fill="#06091c" opacity=".5"/>'
        svg+=f'<text x="64" y="110" fill="{accent}" font-size="32" letter-spacing="3" textLength="900" lengthAdjust="spacingAndGlyphs">{name}</text>'
        svg+=lines(title,64,510,940,80)
        svg+=f'<rect x="64" y="870" width="450" height="96" rx="48" fill="{accent}"/><text x="289" y="932" text-anchor="middle" fill="{primary}" font-size="38" font-weight="700">{price}</text>'
    elif layout=='minimal':
        svg+=f'<text x="540" y="95" text-anchor="middle" fill="{accent}" font-size="28" letter-spacing="2">{name}</text>'
        svg+=art(64,150,952,470)+lines(title,540,730,940,62,3,True)
        svg+=f'<text x="540" y="990" text-anchor="middle" fill="{accent}" font-size="40" font-weight="700">{price}</text>'
    else:
        svg+=f'<text x="56" y="105" fill="{accent}" font-size="30" letter-spacing="3">{name}</text>'
        svg+=art(56,195,455,720)+lines(title,567,330,455,64,5)
        svg+=f'<rect x="567" y="760" width="455" height="96" rx="48" fill="{accent}"/><text x="794" y="822" text-anchor="middle" fill="{primary}" font-size="36" font-weight="700">{price}</text>'
    return svg+'</g></svg>'
def rasterize_brand_card(c, image_b64=None):
    import base64, io, textwrap
    from PIL import Image, ImageDraw, ImageFont

    b=c['snapshot']['brand']
    creative=c.get('results',{}).get('creative',{}).get('output',{})
    writing=c.get('results',{}).get('writing',{}).get('output',{})
    title=creative.get('headline',writing.get('headline','Your next chapter'))
    name=b['name'].upper(); price=b['price']

    def hex2rgb(h, default=(23, 37, 84)):
        try: return tuple(int(h.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
        except: return default

    accent = hex2rgb(creative.get('accent_hex','#38bdf8'), (56, 189, 248))
    primary = hex2rgb(creative.get('primary_hex','#172554'), (23, 37, 84))

    if image_b64 and image_b64.startswith('data:image/png;base64,'):
        try:
            img = Image.open(io.BytesIO(base64.b64decode(image_b64.split(',', 1)[1]))).convert('RGBA')
            w, h = img.size
            img = img.crop((0, 0, w, int(h * 0.955))).resize((1080, 1080))
        except Exception:
            img = None
    else:
        img = None

    if not img:
        img = Image.new('RGBA', (1080, 1080), primary)
        draw_bg = ImageDraw.Draw(img)
        for r in range(540, 0, -4):
            factor = 1.0 - (r / 540.0)
            c_rgb = (int(primary[0] + (accent[0]-primary[0]) * factor * 0.6),
                     int(primary[1] + (accent[1]-primary[1]) * factor * 0.6),
                     int(primary[2] + (accent[2]-primary[2]) * factor * 0.6), 255)
            draw_bg.ellipse([(540 - r, 540 - r), (540 + r, 540 + r)], fill=c_rgb)

    overlay = Image.new('RGBA', (1080, 1080), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    try:
        f_head = ImageFont.truetype("app/Roboto-Bold.ttf", 60)
        f_name = ImageFont.truetype("app/Roboto-Bold.ttf", 30)
        f_price = ImageFont.truetype("app/Roboto-Bold.ttf", 38)
    except:
        f_head = f_name = f_price = ImageFont.load_default()

    draw.rectangle([(0, 0), (1080, 1080)], fill=(6, 9, 28, 80)) # darken
    draw.text((64, 110), name, fill=accent, font=f_name)

    y = 480
    for line in textwrap.wrap(title, width=28):
        draw.text((64, y), line, fill=(255, 255, 255), font=f_head)
        y += 75

    draw.rounded_rectangle([(64, 870), (514, 966)], radius=48, fill=accent)
    draw.text((289, 918), price, fill=primary, font=f_price, anchor="mm")

    out = Image.alpha_composite(img.convert('RGBA'), overlay).convert('RGB')
    buf = io.BytesIO()
    out.save(buf, format='PNG')
    return 'data:image/png;base64,' + base64.b64encode(buf.getvalue()).decode()


class PublisherBot:
    def __init__(self, store): self.store=store

    def publish(self, campaign, approved_hash):
        if content_hash(campaign)!=approved_hash: raise CheckFailure('The approved content version has changed.')
        snapshot=campaign['snapshot']
        if snapshot.get('publishing')!='live':
            return {'mode':'simulation','status':'confirmed_simulated','external_id':'sim-'+campaign['operation_id'],
                    'account':'local-simulator','content_hash':approved_hash,'message':'Confirmed in the simulator. No external post was sent.'}
        platforms=snapshot.get('platforms',[])
        if not platforms: raise CheckFailure('No connected publishing destination is selected for this workflow.')
        from .integrations import Channel
        writing=campaign['results']['writing']['output']
        variants={item['channel']:item for item in writing.get('variants',[])}
        receipts = []
        errors = []
        for platform in platforms:
            operation=campaign['operation_id']+':'+approved_hash+':'+platform
            with self.store.transaction() as db:
                row=db.execute('SELECT * FROM publications WHERE id=?',(operation,)).fetchone()
                if row:
                    if row['status']=='confirmed': receipts.append(json.loads(row['payload'])); continue
                    raise CheckFailure('A previous publication may have reached '+platform+'. Reconcile the account before retrying.')
                db.execute('INSERT INTO publications VALUES(?,?,?)',(operation,'submitting',None))
            variant=variants.get(platform)
            text=(variant['headline']+'\n\n'+variant['body']) if variant else writing['headline']+'\n\n'+writing['caption']
            raw_image = campaign.get('results', {}).get('creative', {}).get('image')
            image_data = rasterize_brand_card(campaign, raw_image)
            try:
                receipt=Channel(platform,self.store.settings().get('social_keys',{})).publish(text, image_b64=image_data)
                with self.store.transaction() as db:
                    db.execute('UPDATE publications SET status=?,payload=? WHERE id=?',('confirmed',json.dumps(receipt),operation))
                receipts.append(receipt)
            except Exception as exc:
                with self.store.transaction() as db:
                    db.execute('DELETE FROM publications WHERE id=? AND status=?',(operation,'submitting'))
                errors.append(f"{platform}: {str(exc)}")

        if not receipts and errors:
            raise CheckFailure("; ".join(errors))

        published_names = [r['platform'] for r in receipts]
        msg = f"Publication confirmed on {', '.join(published_names)}."
        if errors:
            msg += f" (Notice: {'; '.join(errors)})"

        result={'mode':'live','status':'published','receipts':receipts,'content_hash':approved_hash,
                'message': msg}
        return result


def metrics_fixture():
    impressions = 1000
    engagements = 50
    clicks = 20
    return {"mode": "synthetic_fixture", "is_simulation": True, "impressions": impressions, "engagements": engagements, "clicks": clicks,
            "engagement_rate_pct": round(engagements/impressions*100, 2),
            "click_through_rate_pct": round(clicks/impressions*100, 2), "period": "Illustrative fixture; no live measurement period"}
