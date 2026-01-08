# export/exporters.py
# Datapizza v1.4.0 - Funzioni export conversazioni
# ============================================================================

import io
import json
import zipfile
from datetime import datetime
from typing import Dict, Any, List, Optional

from config import VERSION, CONTENT_OPTIONS
from core import load_conversation, get_conversation_filename


def get_messages_for_export(
    messages: List[Dict[str, Any]], 
    content_option: str
) -> List[Dict[str, Any]]:
    """
    Filtra messaggi in base all'opzione di contenuto.
    
    Args:
        messages: Lista completa messaggi
        content_option: Chiave da CONTENT_OPTIONS
        
    Returns:
        Lista messaggi filtrata
    """
    limit = CONTENT_OPTIONS.get(content_option)
    if limit is None:
        return messages
    return messages[-limit:] if len(messages) > limit else messages


def export_to_markdown(
    messages: List[Dict[str, Any]], 
    metadata: Dict[str, Any]
) -> str:
    """
    Esporta conversazione in formato Markdown.
    
    Args:
        messages: Lista messaggi
        metadata: Metadati conversazione
        
    Returns:
        Stringa Markdown
    """
    lines = [
        "# Conversazione LLM", 
        "",
        f"**Data:** {metadata.get('created_at', 'N/A')}", 
        f"**Modello:** {metadata.get('model', 'N/A')}", 
        f"**Messaggi:** {len(messages)}", 
        "", 
        "---", 
        ""
    ]
    
    for msg in messages:
        role = "👤 Tu" if msg.get("role") == "user" else "🤖 AI"
        timestamp = msg.get("timestamp", "")[:19].replace("T", " ")
        content = msg.get("content", "")
        
        lines.extend([
            f"## {role} - {timestamp}", 
            "", 
            content, 
            "", 
            "---", 
            ""
        ])
        
        # Aggiungi fonti se presenti
        sources = msg.get("sources", [])
        if sources:
            lines.extend([
                f"*Fonti: {', '.join(sources)}*",
                "",
            ])
    
    lines.append(f"*Generato con Datapizza v{VERSION} - {datetime.now().strftime('%Y-%m-%d %H:%M')}*")
    return "\n".join(lines)


def export_to_json(
    messages: List[Dict[str, Any]], 
    metadata: Dict[str, Any]
) -> str:
    """
    Esporta conversazione in formato JSON.
    
    Args:
        messages: Lista messaggi
        metadata: Metadati conversazione
        
    Returns:
        Stringa JSON formattata
    """
    export_data = {
        "export_info": {
            "exported_at": datetime.now().isoformat(), 
            "version": VERSION
        }, 
        "conversation": {
            "id": metadata.get("conversation_id"),
            "created_at": metadata.get("created_at"),
            "model": metadata.get("model"),
            "provider": metadata.get("provider"),
            "messages": messages
        }
    }
    return json.dumps(export_data, indent=2, ensure_ascii=False)


def export_to_txt(
    messages: List[Dict[str, Any]], 
    metadata: Dict[str, Any]
) -> str:
    """
    Esporta conversazione in formato TXT.
    
    Args:
        messages: Lista messaggi
        metadata: Metadati conversazione
        
    Returns:
        Stringa testo puro
    """
    lines = [
        "=" * 60, 
        "CONVERSAZIONE LLM", 
        "=" * 60, 
        f"Data: {metadata.get('created_at', 'N/A')}", 
        f"Modello: {metadata.get('model', 'N/A')}", 
        "=" * 60, 
        ""
    ]
    
    for msg in messages:
        role = "Tu" if msg.get("role") == "user" else "AI"
        lines.extend([
            f"[{role}]", 
            msg.get("content", ""), 
            "", 
            "-" * 40, 
            ""
        ])
        
        # Aggiungi fonti se presenti
        sources = msg.get("sources", [])
        if sources:
            lines.extend([
                f"Fonti: {', '.join(sources)}",
                "",
            ])
    
    return "\n".join(lines)


def export_to_pdf(
    messages: List[Dict[str, Any]], 
    metadata: Dict[str, Any]
) -> Optional[bytes]:
    """
    Esporta conversazione in formato PDF.
    
    Richiede reportlab.
    
    Args:
        messages: Lista messaggi
        metadata: Metadati conversazione
        
    Returns:
        Bytes del PDF o None se reportlab non disponibile
    """
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
        from reportlab.lib.styles import getSampleStyleSheet
        
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        styles = getSampleStyleSheet()
        
        story = [
            Paragraph("Conversazione LLM", styles['Title']), 
            Spacer(1, 12),
            Paragraph(f"Data: {metadata.get('created_at', 'N/A')}", styles['Normal']),
            Paragraph(f"Modello: {metadata.get('model', 'N/A')}", styles['Normal']),
            Spacer(1, 20)
        ]
        
        for msg in messages:
            role = "Tu" if msg.get("role") == "user" else "AI"
            content = msg.get("content", "").replace("<", "&lt;").replace(">", "&gt;")
            
            story.append(Paragraph(f"<b>{role}:</b>", styles['Heading2']))
            story.append(Paragraph(content, styles['Normal']))
            
            # Aggiungi fonti se presenti
            sources = msg.get("sources", [])
            if sources:
                story.append(Paragraph(
                    f"<i>Fonti: {', '.join(sources)}</i>", 
                    styles['Normal']
                ))
            
            story.append(Spacer(1, 10))
        
        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()
        
    except ImportError:
        print("⚠️ reportlab non installato. Installa con: pip install reportlab")
        return None
    except Exception as e:
        print(f"❌ Errore creazione PDF: {e}")
        return None


def create_batch_export_zip(
    conversations: List[Dict[str, Any]], 
    export_format: str
) -> Optional[bytes]:
    """
    Crea ZIP con tutte le conversazioni esportate.
    
    Args:
        conversations: Lista info conversazioni (da list_saved_conversations)
        export_format: "Markdown" | "JSON" | "TXT" | "PDF"
        
    Returns:
        Bytes del file ZIP o None se errore
    """
    try:
        buffer = io.BytesIO()
        
        with zipfile.ZipFile(buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            for conv in conversations:
                conv_id = conv.get("id")
                
                # Carica conversazione
                filename = get_conversation_filename(conv_id)
                if not filename.exists():
                    continue
                
                data = load_conversation(conv_id)
                if not data:
                    continue
                
                messages = data.get("messages", [])
                metadata = {
                    "conversation_id": conv_id,
                    "created_at": data.get("created_at", ""),
                    "last_updated": data.get("last_updated", ""),
                    "model": data.get("model", ""),
                    "provider": data.get("provider", ""),
                    "tokens": data.get("stats", {}).get("tokens_estimate", 0)
                }
                
                # Export nel formato selezionato
                if export_format == "Markdown":
                    content = export_to_markdown(messages, metadata)
                    ext = ".md"
                elif export_format == "JSON":
                    content = export_to_json(messages, metadata)
                    ext = ".json"
                elif export_format == "TXT":
                    content = export_to_txt(messages, metadata)
                    ext = ".txt"
                elif export_format == "PDF":
                    content = export_to_pdf(messages, metadata)
                    ext = ".pdf"
                    if content:
                        zip_file.writestr(f"conversation_{conv_id}{ext}", content)
                    continue
                else:
                    continue
                
                # Aggiungi al ZIP
                zip_file.writestr(f"conversation_{conv_id}{ext}", content)
        
        buffer.seek(0)
        return buffer.getvalue()
    
    except Exception as e:
        print(f"❌ Errore creazione ZIP: {e}")
        return None
