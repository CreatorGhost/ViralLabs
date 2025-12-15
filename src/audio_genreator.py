"""
Audio generation service using OpenAI TTS API.
Generates voice-over audio from scripts with various voice styles and tones.
Handles long scripts by splitting into chunks using LangChain and concatenating audio with FFmpeg.
"""

import subprocess
import tempfile
from pathlib import Path
from openai import OpenAI
from uuid import uuid4
from typing import Optional, List
from langchain_text_splitters import RecursiveCharacterTextSplitter


# OpenAI TTS API character limit is 4096
# Using 4000 as safe limit to have margin
MAX_CHAR_LIMIT = 4096
SAFE_CHAR_LIMIT = 4000

# Simple voice mapping - Male/Female to OpenAI voices
VOICES = {
    "male": "ash",
    "female": "coral",
}

# Persona presets with display names and instructions
# These are user-facing categories, not OpenAI voice names
PERSONAS = {
    "storyteller": {
        "name": "Storyteller",
        "description": "Engaging narrator for stories and tales",
        "icon": "📖",
        "instructions": "A normal, natural voice of a storyteller. Engaging and warm with clear articulation. Draw listeners in with your narrative presence.",
    },
    "anime": {
        "name": "Anime",
        "description": "Expressive and animated for anime content",
        "icon": "🎌",
        "instructions": "Speak in a light, fun and animated tone, perfect for anime stories. Use expressive inflections, dramatic pauses, and warm enthusiasm. Channel the energy of anime narration.",
    },
    "tech": {
        "name": "Tech Review",
        "description": "Clear and informative for tech content",
        "icon": "💻",
        "instructions": "Speak in a clear, knowledgeable and engaging tone, perfect for tech reviews and tutorials. Be informative yet accessible. Explain technical concepts with enthusiasm.",
    },
    "tutorial": {
        "name": "Tutorial",
        "description": "Patient and educational for how-to content",
        "icon": "🎓",
        "instructions": "Speak in a clear, patient and educational tone. Perfect for tutorials and how-to content. Pace yourself for comprehension. Be encouraging and supportive.",
    },
    "vlog": {
        "name": "Vlog",
        "description": "Casual and personal for vlogs",
        "icon": "📹",
        "instructions": "Speak in a casual, friendly and personal tone as if talking directly to your audience. Be authentic, relatable and conversational. Share your thoughts naturally.",
    },
    "podcast": {
        "name": "Podcast",
        "description": "Conversational and engaging for podcasts",
        "icon": "🎙️",
        "instructions": "Speak in a conversational, friendly tone as if talking to a close friend. Natural and engaging. Vary your pacing and add thoughtful pauses.",
    },
    "news": {
        "name": "News",
        "description": "Professional and authoritative for news",
        "icon": "📰",
        "instructions": "Speak in a clear, neutral and professional tone, perfect for news delivery. Maintain objectivity and crisp pronunciation. Be authoritative yet accessible.",
    },
    "dramatic": {
        "name": "Dramatic",
        "description": "Theatrical and intense for dramatic content",
        "icon": "🎭",
        "instructions": "Speak with theatrical intensity and emotional depth, perfect for dramatic readings or storytelling. Vary pacing for maximum impact. Build tension and release.",
    },
    "horror": {
        "name": "Horror",
        "description": "Eerie and suspenseful for horror content",
        "icon": "👻",
        "instructions": "Speak in a suspicious, eerie tone as if you're an expert horror storyteller revealing dark secrets. Use dramatic pauses and emphasize chilling details. Create atmosphere.",
    },
    "motivational": {
        "name": "Motivational",
        "description": "Inspiring and energetic for motivation",
        "icon": "🔥",
        "instructions": "Speak with high energy, passion and conviction. Inspire and motivate your listeners. Build momentum and emphasize key points with power and enthusiasm.",
    },
    "meditation": {
        "name": "Meditation",
        "description": "Calm and soothing for relaxation",
        "icon": "🧘",
        "instructions": "Speak in a calm, soothing and gentle tone, perfect for meditation or relaxation. Keep your voice soft, steady and peaceful. Guide listeners to tranquility.",
    },
    "kids": {
        "name": "Kids",
        "description": "Playful and fun for children's content",
        "icon": "🧸",
        "instructions": "Speak in a light, playful and animated tone, perfect for children's content. Use expressive inflections, fun voices, and warm enthusiasm. Keep it engaging and age-appropriate.",
    },
    "documentary": {
        "name": "Documentary",
        "description": "Serious and informative for documentaries",
        "icon": "🎬",
        "instructions": "Speak in a clear, authoritative and measured tone, perfect for documentary narration. Maintain professional gravitas while keeping engagement. Let facts speak through your delivery.",
    },
    "comedy": {
        "name": "Comedy",
        "description": "Witty and humorous for comedy content",
        "icon": "😂",
        "instructions": "Speak in a cheerful, witty and humorous tone, perfect for comedy content. Use playful timing, exaggerated expressions, and comedic pauses. Have fun with delivery.",
    },
}

# Legacy mapping for backward compatibility
VOICE_INSTRUCTIONS = {key: persona["instructions"] for key, persona in PERSONAS.items()}


def get_available_voices() -> list[str]:
    """Get list of available voice options (male/female)."""
    return list(VOICES.keys())


def get_available_personas() -> list[dict]:
    """Get list of available persona presets with full info."""
    return [
        {
            "id": key,
            "name": persona["name"],
            "description": persona["description"],
            "icon": persona["icon"],
        }
        for key, persona in PERSONAS.items()
    ]


def get_persona_ids() -> list[str]:
    """Get list of persona IDs."""
    return list(PERSONAS.keys())


def get_persona_instructions(persona_id: str) -> str:
    """Get instructions for a specific persona."""
    return PERSONAS.get(persona_id, PERSONAS["storyteller"])["instructions"]


def split_script_into_chunks(text: str, chunk_size: int = SAFE_CHAR_LIMIT) -> List[str]:
    """
    Split text into chunks using LangChain's RecursiveCharacterTextSplitter.
    Tries to keep paragraphs together, then sentences, then words.
    
    Args:
        text: The full text to split
        chunk_size: Maximum characters per chunk (default: 4000)
    
    Returns:
        List of text chunks
    """
    if len(text) <= chunk_size:
        return [text]
    
    # Use LangChain's smart splitter
    # It tries separators in order: paragraphs -> sentences -> words
    # NO OVERLAP for TTS - we don't want repeated audio
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=0,  # Zero overlap - no repeated sentences in audio
        separators=["\n\n", "\n", ". ", "! ", "? ", ", ", " ", ""],
        length_function=len,
    )
    
    chunks = splitter.split_text(text)
    return chunks


def generate_single_audio_chunk(
    client: OpenAI,
    text: str,
    output_path: Path,
    voice: str,
    instructions: str,
) -> bool:
    """Generate audio for a single text chunk using gpt-4o-mini-tts."""
    try:
        with client.audio.speech.with_streaming_response.create(
            model="gpt-4o-mini-tts",
            voice=voice,
            input=text,
            instructions=instructions,
        ) as response:
            response.stream_to_file(str(output_path))
        return True
    except Exception as e:
        print(f"Error generating audio chunk: {e}")
        return False


def concatenate_audio_files(audio_paths: List[Path], output_path: Path) -> bool:
    """Concatenate multiple audio files into one seamless file using FFmpeg."""
    try:
        # Create a temporary file listing all audio files for FFmpeg concat
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            for path in audio_paths:
                # FFmpeg concat format: file 'path'
                f.write(f"file '{path}'\n")
            concat_list_path = f.name

        # Use FFmpeg to concatenate without re-encoding (fast & lossless)
        cmd = [
            'ffmpeg',
            '-y',  # Overwrite output file
            '-f', 'concat',
            '-safe', '0',
            '-i', concat_list_path,
            '-c', 'copy',  # Copy codec (no re-encoding)
            str(output_path)
        ]

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True
        )

        # Clean up the concat list file
        Path(concat_list_path).unlink(missing_ok=True)

        if result.returncode != 0:
            print(f"FFmpeg error: {result.stderr}")
            return False

        return True
    except FileNotFoundError:
        print("FFmpeg not found. Please install FFmpeg.")
        return False
    except Exception as e:
        print(f"Error concatenating audio: {e}")
        return False


def generate_audio(
    script: str,
    output_dir: Path,
    voice: str = "female",
    persona: str = "storyteller",
    custom_instructions: Optional[str] = None,
    filename: Optional[str] = None,
) -> dict:
    """
    Generate audio from script text using OpenAI gpt-4o-mini-tts API.
    Automatically handles long scripts by splitting and concatenating.
    
    Args:
        script: The text content to convert to speech
        output_dir: Directory to save the audio file
        voice: Voice gender to use (male or female)
        persona: Persona preset ID (storyteller, anime, tech, etc.)
        custom_instructions: Custom voice instructions (overrides persona if provided)
        filename: Optional custom filename (without extension)
    
    Returns:
        dict with success status, file path, and metadata
    """
    try:
        client = OpenAI()
        
        # Ensure output directory exists
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Resolve voice - map male/female to OpenAI voices
        resolved_voice = VOICES.get(voice.lower(), "coral")  # Default to female (coral)
        
        # Get instructions - custom takes precedence over persona preset
        if custom_instructions:
            instructions = custom_instructions
        else:
            instructions = get_persona_instructions(persona)
        
        # Get persona info for response
        persona_info = PERSONAS.get(persona, PERSONAS["storyteller"])
        
        # Generate filename
        if not filename:
            filename = f"audio_{uuid4().hex[:8]}"
        
        output_path = output_dir / f"{filename}.mp3"
        script_text = script.strip()
        
        # Check if we need to split the script
        if len(script_text) <= SAFE_CHAR_LIMIT:
            # Simple case - single request
            print(f"🎙️ Generating audio: voice='{voice}' ({resolved_voice}), persona='{persona}' ({len(script_text)} chars)")
            with client.audio.speech.with_streaming_response.create(
                model="gpt-4o-mini-tts",
                voice=resolved_voice,
                input=script_text,
                instructions=instructions,
            ) as response:
                response.stream_to_file(str(output_path))
            
            return {
                "success": True,
                "filepath": str(output_path),
                "filename": f"{filename}.mp3",
                "voice": voice,
                "persona": persona,
                "persona_name": persona_info["name"],
                "model": "gpt-4o-mini-tts",
                "script_length": len(script_text),
                "chunks_processed": 1,
            }
        
        # Long script - split into chunks using LangChain
        chunks = split_script_into_chunks(script_text, SAFE_CHAR_LIMIT)
        print(f"📝 Script ({len(script_text)} chars) split into {len(chunks)} chunks")
        
        # Generate audio for each chunk
        temp_audio_paths = []
        
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            for i, chunk in enumerate(chunks):
                chunk_path = temp_path / f"chunk_{i:03d}.mp3"
                print(f"🎙️ Generating chunk {i+1}/{len(chunks)} ({len(chunk)} chars) - {persona}")
                
                success = generate_single_audio_chunk(
                    client=client,
                    text=chunk,
                    output_path=chunk_path,
                    voice=resolved_voice,
                    instructions=instructions,
                )
                
                if not success:
                    return {
                        "success": False,
                        "error": f"Failed to generate audio for chunk {i+1}",
                    }
                
                temp_audio_paths.append(chunk_path)
            
            # Concatenate all audio chunks
            print(f"🔗 Concatenating {len(temp_audio_paths)} audio chunks...")
            if not concatenate_audio_files(temp_audio_paths, output_path):
                return {
                    "success": False,
                    "error": "Failed to concatenate audio chunks",
                }
        
        print(f"✅ Audio generated: {output_path}")
        return {
            "success": True,
            "filepath": str(output_path),
            "filename": f"{filename}.mp3",
            "voice": voice,
            "persona": persona,
            "persona_name": persona_info["name"],
            "model": "gpt-4o-mini-tts",
            "script_length": len(script_text),
            "chunks_processed": len(chunks),
        }
        
    except Exception as e:
        print(f"❌ Audio generation error: {e}")
        return {
            "success": False,
            "error": str(e),
        }


def generate_audio_from_file(
    script_path: Path,
    output_dir: Path,
    voice: str = "female",
    persona: str = "storyteller",
    custom_instructions: Optional[str] = None,
    filename: Optional[str] = None,
) -> dict:
    """
    Generate audio from a script file.
    
    Args:
        script_path: Path to the script text file
        output_dir: Directory to save the audio file
        voice: Voice gender (male or female)
        persona: Persona preset ID
        custom_instructions: Custom voice instructions
        filename: Optional custom filename
    
    Returns:
        dict with success status, file path, and metadata
    """
    try:
        with open(script_path, "r", encoding="utf-8") as f:
            script = f.read()
        
        return generate_audio(
            script=script,
            output_dir=output_dir,
            voice=voice,
            persona=persona,
            custom_instructions=custom_instructions,
            filename=filename,
        )
    except FileNotFoundError:
        return {
            "success": False,
            "error": f"Script file not found: {script_path}",
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
        }


# CLI support for standalone usage
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 4:
        print("Usage: python audio_generator.py <script_file> <persona> <voice>")
        print(f"Available personas: {', '.join(get_persona_ids())}")
        print(f"Available voices: {', '.join(get_available_voices())}")
        sys.exit(1)
    
    file_name = sys.argv[1]
    persona_id = sys.argv[2]
    voice_type = sys.argv[3]
    
    audio_dir = Path(__file__).parent / "audio"
    script_file_path = Path(__file__).parent / file_name
    
    result = generate_audio_from_file(
        script_path=script_file_path,
        output_dir=audio_dir,
        voice=voice_type,
        persona=persona_id,
    )
    
    if result["success"]:
        print(f"✅ Audio generated: {result['filepath']}")
        print(f"   Voice: {result['voice']}, Persona: {result['persona_name']}")
        if result.get("chunks_processed", 1) > 1:
            print(f"   Processed {result['chunks_processed']} chunks")
    else:
        print(f"❌ Error: {result['error']}")
