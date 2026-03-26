"""
PDF Report Generation Service
Creates bank loan application quality PDF reports for farmers
"""
import os
import io
from datetime import datetime
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


def generate_pdf_report(query, recommendation) -> bytes:
    """
    Generate a comprehensive PDF report for bank loan applications.
    
    Args:
        query: FarmerQuery model instance
        recommendation: CropRecommendation model instance
    
    Returns:
        PDF file as bytes
    """
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import inch, cm
        from reportlab.lib import colors
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
        from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
        from reportlab.pdfbase import pdfmetrics
        
        buffer = io.BytesIO()
        
        # Setup document
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=1.5*cm,
            leftMargin=1.5*cm,
            topMargin=2*cm,
            bottomMargin=2*cm,
            title="AI Crop Recommendation Report",
            author="Kisan AI - Crop Recommendation System"
        )
        
        # Colors
        GREEN = colors.Color(0.18, 0.49, 0.20)       # Dark green
        LIGHT_GREEN = colors.Color(0.85, 0.95, 0.85)  # Light green
        DARK_GREY = colors.Color(0.2, 0.2, 0.2)
        GOLD = colors.Color(0.85, 0.65, 0.12)
        BLUE = colors.Color(0.12, 0.29, 0.55)
        LIGHT_BLUE = colors.Color(0.88, 0.93, 0.98)
        
        styles = getSampleStyleSheet()
        
        # Custom styles
        title_style = ParagraphStyle(
            'CustomTitle', parent=styles['Title'],
            fontSize=22, textColor=GREEN, fontName='Helvetica-Bold',
            alignment=TA_CENTER, spaceAfter=6
        )
        subtitle_style = ParagraphStyle(
            'CustomSubtitle', parent=styles['Normal'],
            fontSize=12, textColor=DARK_GREY, alignment=TA_CENTER, spaceAfter=4
        )
        heading_style = ParagraphStyle(
            'Heading', parent=styles['Heading2'],
            fontSize=14, textColor=GREEN, fontName='Helvetica-Bold',
            spaceBefore=12, spaceAfter=6, borderPad=4
        )
        normal_style = ParagraphStyle(
            'Normal', parent=styles['Normal'],
            fontSize=10, leading=14, spaceAfter=4, textColor=DARK_GREY
        )
        bold_style = ParagraphStyle(
            'Bold', parent=styles['Normal'],
            fontSize=10, fontName='Helvetica-Bold', textColor=DARK_GREY
        )
        
        story = []
        
        # ====== HEADER ======
        story.append(Paragraph("🌾 KISAN AI - CROP RECOMMENDATION REPORT", title_style))
        story.append(Paragraph("AI-Based Agricultural Advisory System | किसान एआई - फसल सुझाव रिपोर्ट", subtitle_style))
        story.append(Paragraph(f"Report Generated: {datetime.now().strftime('%d %B %Y, %I:%M %p IST')}", subtitle_style))
        story.append(HRFlowable(width="100%", thickness=3, color=GREEN, spaceAfter=10))
        
        # PURPOSE BOX  
        purpose_data = [["PURPOSE OF REPORT / रिपोर्ट का उद्देश्य"]]
        purpose_table = Table(purpose_data, colWidths=[17*cm])
        purpose_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), LIGHT_GREEN),
            ('TEXTCOLOR', (0, 0), (-1, -1), GREEN),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('PADDING', (0, 0), (-1, -1), 8),
            ('ROUNDEDCORNERS', [5, 5, 5, 5]),
        ]))
        story.append(purpose_table)
        story.append(Paragraph(
            "This report has been prepared by an AI-based agricultural advisory system to assist the farmer in crop selection, "
            "yield estimation, and market price forecasting. This document may be submitted to financial institutions for "
            "agricultural loan applications.",
            normal_style
        ))
        story.append(Spacer(1, 0.3*cm))
        
        # ====== FARMER INFORMATION ======
        story.append(Paragraph("1. FARMER & FARM INFORMATION / किसान एवं खेत की जानकारी", heading_style))
        
        farmer_data = [
            ["Field", "Details", "Field", "Details"],
            ["Location / स्थान", query.location, "Season / ऋतु", query.get_season_display()],
            ["Soil Type / मिट्टी", query.get_soil_type_display(), "Water / जल", query.get_water_availability_display()],
            ["Land Area / क्षेत्र", f"{query.land_area} Acres", "Language", query.get_language_display()],
            ["Date of Query", query.created_at.strftime('%d-%m-%Y'), "Report ID", f"KAI-{query.id:06d}"],
        ]
        
        farmer_table = Table(farmer_data, colWidths=[4.5*cm, 5*cm, 4.5*cm, 3.2*cm])
        farmer_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), GREEN),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('BACKGROUND', (0, 1), (0, -1), LIGHT_GREEN),
            ('BACKGROUND', (2, 1), (2, -1), LIGHT_GREEN),
            ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (2, 1), (2, -1), 'Helvetica-Bold'),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('PADDING', (0, 0), (-1, -1), 6),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.Color(0.97, 0.97, 0.97)]),
        ]))
        story.append(farmer_table)
        story.append(Spacer(1, 0.3*cm))
        
        # ====== SUMMARY ======
        story.append(Paragraph("2. AI RECOMMENDATION SUMMARY / एआई सुझाव सारांश", heading_style))
        story.append(Paragraph(recommendation.summary, normal_style))
        story.append(Spacer(1, 0.3*cm))
        
        # ====== CROP RECOMMENDATIONS ======
        story.append(Paragraph("3. RECOMMENDED CROPS / अनुशंसित फसलें", heading_style))
        
        crops = recommendation.crops_data
        for i, crop in enumerate(crops[:3], 1):
            # Crop header
            crop_header = [
                [f"#{i} {crop.get('name', 'Crop')} ({crop.get('hindi_name', '')}) - Confidence: {crop.get('confidence', 0)}%"]
            ]
            header_table = Table(crop_header, colWidths=[17*cm])
            header_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), GREEN if i == 1 else BLUE),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.white),
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 11),
                ('PADDING', (0, 0), (-1, -1), 8),
            ]))
            story.append(header_table)
            
            crop_details = [
                ["Parameter", "Value", "Parameter", "Value"],
                ["Duration", f"{crop.get('duration_days', 'N/A')} days", "Yield/Acre", crop.get('estimated_yield_per_acre', 'N/A')],
                ["Sowing Time", crop.get('sowing_time', 'N/A'), "Harvest Time", crop.get('harvesting_time', 'N/A')],
                ["Water Needed", crop.get('water_requirement', 'N/A'), "Fertilizer", crop.get('fertilizer', 'N/A')],
            ]
            
            detail_table = Table(crop_details, colWidths=[3.5*cm, 5*cm, 4*cm, 4.7*cm])
            detail_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), LIGHT_GREEN if i == 1 else LIGHT_BLUE),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
                ('FONTNAME', (2, 1), (2, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 8.5),
                ('PADDING', (0, 0), (-1, -1), 5),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.Color(0.97, 0.97, 0.97)]),
            ]))
            story.append(detail_table)
            
            if crop.get('pros'):
                pros_text = "✓ " + "  ✓ ".join(crop['pros'][:3])
                story.append(Paragraph(f"<b>Benefits:</b> {pros_text}", normal_style))
            
            if crop.get('care_tips'):
                story.append(Paragraph(f"<b>Care Tips:</b> {crop['care_tips']}", normal_style))
            
            story.append(Spacer(1, 0.3*cm))
        
        # ====== MANDI PRICE FORECAST ======
        story.append(Paragraph("4. MANDI PRICE FORECAST / मंडी मूल्य पूर्वानुमान", heading_style))
        
        price_data = [["Crop / फसल", "Current Price\n(₹/Quintal)", "Forecast at\nHarvest", "MSP 2024-25", "Trend", "Best Market"]]
        
        for p in recommendation.mandi_prices_data[:3]:
            trend_symbol = "📈 Rising" if p.get('trend') == 'rising' else ("📉 Falling" if p.get('trend') == 'falling' else "➡ Stable")
            price_data.append([
                p.get('crop', 'N/A'),
                f"₹{p.get('current_price_per_quintal', 0):,}",
                f"₹{p.get('predicted_price_at_harvest', 0):,}",
                f"₹{p.get('msp', 0):,}",
                trend_symbol,
                p.get('best_market', 'N/A')
            ])
        
        price_table = Table(price_data, colWidths=[3.5*cm, 2.5*cm, 2.5*cm, 2.5*cm, 2.5*cm, 3.7*cm])
        price_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), GOLD),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 8.5),
            ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
            ('PADDING', (0, 0), (-1, -1), 5),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.Color(0.99, 0.98, 0.92)]),
        ]))
        story.append(price_table)
        story.append(Spacer(1, 0.3*cm))
        
        # ====== INCOME ESTIMATE ======
        story.append(Paragraph("5. ESTIMATED INCOME / अनुमानित आय", heading_style))
        
        income_data = [["Crop", "Yield/Acre", "Price (₹/Q)", "Gross Income/Acre", "Est. Cost/Acre", "Net Profit/Acre"]]
        crops_data = recommendation.crops_data
        prices_data = recommendation.mandi_prices_data
        
        for i, (crop, price) in enumerate(zip(crops_data[:3], prices_data[:3])):
            yield_str = crop.get('estimated_yield_per_acre', '15-20 quintals')
            try:
                yield_low = float(yield_str.split('-')[0].replace('quintals', '').strip())
                yield_avg = yield_low + 3
            except:
                yield_avg = 18
            
            price_val = price.get('predicted_price_at_harvest', 2500)
            gross = int(yield_avg * price_val)
            cost = int(gross * 0.4)
            net = gross - cost
            
            income_data.append([
                crop.get('name', 'Crop'),
                yield_str,
                f"₹{price_val:,}",
                f"₹{gross:,}",
                f"₹{cost:,}",
                f"₹{net:,}"
            ])
        
        income_table = Table(income_data, colWidths=[3*cm, 3*cm, 2.5*cm, 3*cm, 2.5*cm, 3.2*cm])
        income_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), BLUE),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 8.5),
            ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('PADDING', (0, 0), (-1, -1), 5),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, LIGHT_BLUE]),
            ('FONTNAME', (5, 1), (5, -1), 'Helvetica-Bold'),
            ('TEXTCOLOR', (5, 1), (5, -1), GREEN),
        ]))
        story.append(income_table)
        story.append(Spacer(1, 0.3*cm))
        
        # ====== FARMING TIPS ======
        story.append(Paragraph("6. FARMING TIPS & GOVERNMENT SCHEMES / सरकारी योजनाएं", heading_style))
        
        tips = recommendation.farming_tips
        if tips:
            for tip in tips.split('\n'):
                if tip.strip():
                    story.append(Paragraph(tip.strip(), normal_style))
        
        schemes = recommendation.crops_data  # We'll use government_schemes from the data
        
        # ====== DISCLAIMER ======
        story.append(Spacer(1, 0.5*cm))
        story.append(HRFlowable(width="100%", thickness=1, color=colors.grey, spaceAfter=8))
        disclaimer_style = ParagraphStyle(
            'Disclaimer', parent=styles['Normal'],
            fontSize=8, textColor=colors.grey, alignment=TA_CENTER
        )
        story.append(Paragraph(
            "DISCLAIMER: This report is generated by an AI system for agricultural advisory purposes. "
            "Actual crop yields and market prices may vary. Please consult your local Krishi Vigyan Kendra (KVK) "
            "or Agriculture Department for official guidance. This report is not a guarantee of income. | "
            "Report ID: KAI-{:06d} | Generated: {}".format(query.id, datetime.now().strftime('%d-%m-%Y')),
            disclaimer_style
        ))
        
        # Build PDF
        doc.build(story)
        pdf_bytes = buffer.getvalue()
        buffer.close()
        return pdf_bytes
    
    except Exception as e:
        logger.error(f"PDF generation error: {e}")
        raise
