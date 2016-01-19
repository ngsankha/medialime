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
  global music_library, library_index, songs
  music_library = str(preferences.get("music_library"))
  inbuilt = [
    ["Set Music Library", "Current Directory: " + music_library],
  ]
  if (paused):
    inbuilt.append(["Play", "Now playing: " + current_playing])
  else:
    inbuilt.append(["Pause", "Now playing: " + current_playing])
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

def selected_option(index):
  global current_playing, mplayer_process, paused
  if (index < 2):
    if (index == 1 and mplayer_process != -1 and mplayer_process.poll() is None):
      if (paused):
        paused = False
      else:
        paused = True
      mplayer_process.stdin.write(b"pause\n")
      mplayer_process.stdin.flush()
    else:
      sublime.active_window().show_input_panel("Music library", music_library, update_music_library, None, None)
  else:
    if (mplayer_process != -1 and mplayer_process.poll() is not None):
      mplayer_process.kill()
    index -= 2
    current_playing = songs[index]
    mplayer_process = subprocess.Popen(["/usr/local/bin/mplayer", "-slave", library_index[current_playing]], stdin=subprocess.PIPE)
    paused = False
    sublime.status_message("Now playing: " + current_playing)

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
