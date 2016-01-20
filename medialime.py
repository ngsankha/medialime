import os, subprocess
import sublime, sublime_plugin

class MedialimeCommand(sublime_plugin.WindowCommand):
  def run(self):
    sublime.status_message("Indexing library ...")
    show_menu()

music_library = ""
current_playing = "None"
mplayer_process = -1
library_index = {}
songs = []
paused = False
preferences = sublime.load_settings("Preferences.sublime-settings")

def show_menu():
  global preferences, music_library, library_index, songs
  preferences = sublime.load_settings("Preferences.sublime-settings")
  music_library = str(preferences.get("music_library"))
  inbuilt = []
  if (paused):
    inbuilt.append(["Play", "Now playing: " + current_playing])
  else:
    inbuilt.append(["Pause", "Now playing: " + current_playing])
  inbuilt += [
    ["Set Music Library", "Current Directory: " + music_library],
    ["Set mplayer path", str(preferences.get("mplayer_path", "mplayer"))]
  ]
  library_index = index_files(music_library)
  songs = list(library_index.keys())
  listing = inbuilt + songs
  sublime.active_window().show_quick_panel(listing, selected_option)
  sublime.status_message("")

def update_music_library(new_location):
  global music_library
  music_library = new_location
  preferences.set("music_library", new_location)
  sublime.save_settings("Preferences.sublime-settings")

def update_mplayer_path(new_path):
  preferences.set("mplayer_path", new_path)
  sublime.save_settings("Preferences.sublime-settings")

def selected_option(index):
  global current_playing, mplayer_process, paused
  if (index < 3):
    if (index == 0 and mplayer_process != -1 and mplayer_process.poll() is None):
      if (paused):
        paused = False
      else:
        paused = True
      mplayer_process.stdin.write(b"pause\n")
      mplayer_process.stdin.flush()
    elif (index == 1):
      sublime.active_window().show_input_panel("Music library", music_library, update_music_library, None, None)
    else:
      sublime.active_window().show_input_panel("mplayer_path", preferences.get("mplayer_path", "mplayer"), update_mplayer_path, None, None)
  else:
    if (mplayer_process != -1 and mplayer_process.poll() is None):
      mplayer_process.kill()
    index -= 3
    try:
      mplayer_process = subprocess.Popen([preferences.get("mplayer_path", "mplayer"), "-slave", library_index[songs[index]]], stdin=subprocess.PIPE)
      current_playing = songs[index]
      paused = False
      sublime.status_message("Now playing: " + current_playing)
    except Exception:
      pass

def index_files(music_library):
  library_index = {}
  for root, dirs, files in os.walk(music_library):
    for f in files:
      filename, file_ext = os.path.splitext(os.path.join(root, f))
      if file_ext == ".mp3":
        library_index[f] = os.path.join(root, f)
  return library_index

def plugin_unloaded():
  if mplayer_process != -1:
    mplayer_process.kill()
