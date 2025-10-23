# i18n_manager.py
"""
Internationalization (i18n) Manager for Mowbot Fleet Dashboard
Supports multiple languages with easy extensibility
"""

import json
import os
from typing import Dict, Any, Optional, List
from pathlib import Path
import streamlit as st
from config import load_config, save_config

class I18nManager:
    """Manages internationalization for the application"""
    
    def __init__(self, translations_dir: str = "translations"):
        self.translations_dir = Path(translations_dir)
        self.translations: Dict[str, Dict[str, Any]] = {}
        self.current_language = "en"  # Default to English
        self.fallback_language = "en"
        
        # Load all available translations
        self._load_translations()
        
        # Initialize session state for language preference
        if "language" not in st.session_state:
            st.session_state.language = self._load_saved_language()
    
    def _load_translations(self):
        """Load all translation files from the translations directory"""
        if not self.translations_dir.exists():
            print(f"⚠️ Translations directory not found: {self.translations_dir}")
            return
            
        for translation_file in self.translations_dir.glob("*.json"):
            if translation_file.name == "template.json":
                continue  # Skip template file
                
            language_code = translation_file.stem
            try:
                with open(translation_file, 'r', encoding='utf-8') as f:
                    self.translations[language_code] = json.load(f)
                print(f"✅ Loaded translations for: {language_code}")
            except Exception as e:
                print(f"❌ Failed to load translations for {language_code}: {e}")
    
    def _load_saved_language(self) -> str:
        """Load saved language preference from config"""
        try:
            config = load_config()
            saved_language = config.get("general", {}).get("language", None)
            
            if saved_language and saved_language in self.translations:
                print(f"🌍 Loaded saved language preference: {saved_language}")
                return saved_language
            else:
                print(f"🌍 No valid saved language found, using default: {self.fallback_language}")
                return self.fallback_language
        except Exception as e:
            print(f"⚠️ Failed to load saved language: {e}")
            return self.fallback_language
    
    def _save_language_preference(self, language_code: str):
        """Save language preference to config"""
        try:
            config = load_config()
            
            # Ensure general section exists
            if "general" not in config:
                config["general"] = {}
            
            # Save language preference
            config["general"]["language"] = language_code
            
            # Save to config file
            save_config(config)
            print(f"💾 Saved language preference: {language_code}")
            
        except Exception as e:
            print(f"❌ Failed to save language preference: {e}")
    
    def _detect_language(self) -> str:
        """Detect user's preferred language (fallback method)"""
        # Try to get language from browser (if available)
        try:
            # This is a simplified detection - in production you might want more sophisticated detection
            return self.current_language
        except:
            return self.fallback_language
    
    def get_available_languages(self) -> Dict[str, str]:
        """Get list of available languages with their display names"""
        language_names = {
            "en": "English",
            "ko": "한국어",
            "ja": "日本語",
            "zh": "中文",
            "fr": "Français",
            "de": "Deutsch",
            "es": "Español"
        }
        
        available = {}
        for lang_code in self.translations.keys():
            if lang_code in language_names:
                available[lang_code] = language_names[lang_code]
            else:
                available[lang_code] = lang_code.upper()
        
        return available
    
    def set_language(self, language_code: str, save_preference: bool = True):
        """Set the current language and optionally save preference"""
        if language_code in self.translations:
            self.current_language = language_code
            st.session_state.language = language_code
            
            # Save language preference to config
            if save_preference:
                self._save_language_preference(language_code)
            
            print(f"🌍 Language set to: {language_code}")
        else:
            print(f"⚠️ Language not available: {language_code}")
    
    def get_current_language(self) -> str:
        """Get the current language"""
        return st.session_state.get("language", self.current_language)
    
    def get_saved_language(self) -> str:
        """Get the saved language preference from config"""
        try:
            config = load_config()
            return config.get("general", {}).get("language", self.fallback_language)
        except:
            return self.fallback_language
    
    def reset_language_preference(self):
        """Reset language preference to default"""
        try:
            config = load_config()
            if "general" in config and "language" in config["general"]:
                del config["general"]["language"]
                save_config(config)
                print("🔄 Language preference reset to default")
        except Exception as e:
            print(f"❌ Failed to reset language preference: {e}")
    
    def t(self, key: str, **kwargs) -> str:
        """
        Get translated text for a key
        
        Args:
            key: Translation key (e.g., "broker.title")
            **kwargs: Format parameters for string formatting
            
        Returns:
            Translated text or key if translation not found
        """
        current_lang = self.get_current_language()
        
        # Try to get translation from current language
        translation = self._get_nested_value(self.translations.get(current_lang, {}), key)
        
        # Fallback to English if not found
        if not translation and current_lang != self.fallback_language:
            translation = self._get_nested_value(self.translations.get(self.fallback_language, {}), key)
        
        # If still not found, return the key
        if not translation:
            print(f"⚠️ Translation missing for key: {key} (language: {current_lang})")
            return key
        
        # Format the translation with any provided parameters
        try:
            return translation.format(**kwargs)
        except (KeyError, ValueError) as e:
            print(f"⚠️ Formatting error for key {key}: {e}")
            return translation
    
    def _get_nested_value(self, data: Dict[str, Any], key: str) -> Optional[str]:
        """Get nested value from dictionary using dot notation"""
        keys = key.split('.')
        current = data
        
        for k in keys:
            if isinstance(current, dict) and k in current:
                current = current[k]
            else:
                return None
        
        return current if isinstance(current, str) else None
    
    def add_language(self, language_code: str, translations: Dict[str, Any]):
        """Add a new language programmatically"""
        self.translations[language_code] = translations
        print(f"✅ Added language: {language_code}")
    
    def save_language_file(self, language_code: str):
        """Save current language translations to file"""
        if language_code in self.translations:
            file_path = self.translations_dir / f"{language_code}.json"
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(self.translations[language_code], f, ensure_ascii=False, indent=2)
                print(f"✅ Saved translations to: {file_path}")
            except Exception as e:
                print(f"❌ Failed to save translations: {e}")
    
    def get_language_info(self, language_code: str) -> Dict[str, Any]:
        """Get information about a specific language"""
        if language_code not in self.translations:
            return {"exists": False}
        
        translation_count = self._count_translations(self.translations[language_code])
        return {
            "exists": True,
            "translation_count": translation_count,
            "language_code": language_code
        }
    
    def _count_translations(self, data: Dict[str, Any]) -> int:
        """Count total number of translation keys"""
        count = 0
        for value in data.values():
            if isinstance(value, dict):
                count += self._count_translations(value)
            else:
                count += 1
        return count

# Global i18n manager instance
i18n = I18nManager()

# Convenience function for easy access
def t(key: str, **kwargs) -> str:
    """Convenience function to get translated text"""
    return i18n.t(key, **kwargs)

# Language selector component
def render_language_selector():
    """Render language selector component with saved preference info"""
    available_languages = i18n.get_available_languages()
    current_language = i18n.get_current_language()
    saved_language = i18n.get_saved_language()
    
    # Create language options
    language_options = list(available_languages.keys())
    language_labels = [f"{available_languages[lang]} ({lang.upper()})" for lang in language_options]
    
    # Find current selection index
    try:
        current_index = language_options.index(current_language)
    except ValueError:
        current_index = 0
    
    # Show saved preference info
    if saved_language and saved_language != current_language:
        st.info(t("settings.language_preference_saved", language=available_languages.get(saved_language, saved_language)))
    
    # Render selectbox
    selected_label = st.selectbox(
        "🌍 Language / 언어",
        options=language_labels,
        index=current_index,
        key="language_selector",
        help=t("settings.language_auto_save")
    )
    
    # Extract language code from selection
    selected_language = language_options[language_labels.index(selected_label)]
    
    # Update language if changed
    if selected_language != current_language:
        i18n.set_language(selected_language)
        st.success(t("settings.language_saved", language=available_languages[selected_language]))
        st.rerun()
    
    return selected_language
