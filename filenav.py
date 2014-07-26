# -*- coding: utf-8 -*-
###############################################################################
# filenav by dgelessus
# http://github.com/dgelessus/pythonista-scripts/blob/master/filenav.py
###############################################################################
# This is a standalone script, no additional files are necessary.
# By default, the navigator starts at ~ (the app sandbox root). A different
# root folder can be passed as a runtime argument - tap and hold the play icon.
# Execution from other scripts is also supported using filenav.run(path)
###############################################################################
# A note on Shellista integration:
# Shellista is expected to be importable, i. e. located in the root folder
# of Pythonista's Script Library, site-packages, or another folder in PATH.
# The original Shellista by pudquick as well as transistor1's have been tested
# and are known to work. Other forks should also be compatible, as long as
# the main code does not differ significantly.
# To use ShellistaExt by briarfox, the module and main class name need to be
# changed from Shellista to ShellistaExt and Shell to Shellista respectively.
# The plugins folder needs to be moved into PATH along with the main script.
###############################################################################

import console   # for Quick Look and Open In
import datetime  # to format timestamps from os.stat()
import editor    # to open files
import errno     # for OSError codes
import os        # to navigate the file structure
import os.path   # ditto
import PIL       # for thumbnail creation
import PIL.Image # ditto
import shutil    # to copy files
import stat      # to analyze stat results
import sys       # for sys.argv
import time      # to sleep in certain situations and avoid hangs
import ui        # duh
try:             # to save PIL images to string
    import cStringIO as StringIO
except ImportError:
    import StringIO

def full_path(path):
    # Return absolute path with expanded ~s, input path assumed relative to cwd
    return os.path.realpath(os.path.abspath(os.path.expanduser(path)))

def rel_to_docs(path):
    # Return path relative to script library (~/Documents)
    return os.path.relpath(full_path(path), os.path.expanduser("~/Documents"))

# get location of current script, fall back to ~ if necessary
if sys.argv[0] == "prompt":
    SCRIPT_ROOT = full_path("~")
else:
    SCRIPT_ROOT = os.path.dirname(sys.argv[0])

# dict of known file types and extensions
FILE_TYPES = {
              "app":       ("app", "exe", "nib", "pytheme", "pyui"),
              "archive":   ("bundle", "bz2", "cpgz", "dmg", "gz", "gzip", "rar", "tar", "tgz", "z", "zip"),
              "audio":     ("aac", "aif", "aiff", "caf", "m4a", "m4r", "mp3", "ogg", "wav"),
              "code":      ("c", "command", "cpp", "css", "h", "hpp", "js", "json", "makefile", "pxd", "pxi", "py", "pyx", "sh", "src"),
              "code_tags": ("htm", "html", "php", "plist", "xml"),
              "data":      ("bin", "cache", "dat", "db", "pkl", "pyc", "pyo"),
              "font":      ("fon", "otf", "ttc", "ttf"),
              "git":       ("git", "gitignore"),
              "image":     ("bmp", "gif", "icns", "itunesartwork", "jpg", "jpeg", "png"),
              "text":      ("authors", "build", "cfg", "changelog", "changes", "clslog", "contribs", "contributors", "copyright", "copyrights", "csv", "doc", "docx", "dot", "dotx", "hgignore", "hgsubstate", "hgtags", "in", "ini", "install", "installation", "license", "md", "odf", "odt", "pages", "pdf", "readme", "rst", "rtf", "txt", "version", "yml"),
              "video":     ("avi", "m4v", "mov", "mp4"),
              }

# dict of all file type icons
FILE_ICONS = {
              "app":       ui.Image.named("../FileUI"),
              "archive":   ui.Image.named("ionicons-filing-32"),
              "audio":     ui.Image.named("ionicons-ios7-musical-notes-32"),
              "code":      ui.Image.named("../FilePY"),
              "code_tags": ui.Image.named("ionicons-code-32"),
              "data":      ui.Image.named("ionicons-social-buffer-32"),
              "file":      ui.Image.named("ionicons-document-32"),
              #"folder":    ui.Image.named("../Folder"),
              "folder":    ui.Image.named("ionicons-folder-32"),
              "font":      ui.Image.named("../fonts-selected"),
              "git":       ui.Image.named("ionicons-social-github-32"),
              #"image":     ui.Image.named("../FileImage"),
              "image":     ui.Image.named("ionicons-image-32"),
              #"text":      ui.Image.named("../FileOther"),
              "text":      ui.Image.named("ionicons-document-text-32"),
              "video":     ui.Image.named("ionicons-ios7-film-outline-32"),
              }

class FileItem(object):
    # object representation of a file and its properties
    def __init__(self, path):
        # init
        self.path = path
        self.refresh()
    
    def refresh(self):
        # refresh all properties
        self.path = full_path(self.path)
        self.rel_to_docs = rel_to_docs(self.path)
        self.location, self.name = os.path.split(self.path)
        self.nameparts = self.name.rsplit(".")
        self.stat = os.stat(self.path)
        
        if os.path.isdir(self.path):
            self.basetype = 0
            self.filetype = "folder"
            self.contents = os.listdir(self.path)
        else:
            self.basetype = 1
            self.filetype = "file"
            self.contents = []
        
        for part in self.nameparts:
            for type in FILE_TYPES:
                if part.lower() in FILE_TYPES[type]:
                    self.filetype = type
    
    def __repr__(self):
        # repr(self) and str(self)
        return "filenav.FileItem(" + self.path + ")"
    
    def __eq__(self, other):
        # self == other
        if isinstance(other, FileItem):
            return os.path.samefile(self.path, other.path)
        else:
            return False
    
    def __ne__(self, other):
        # self != other
        if isinstance(other, FileItem):
            return not os.path.samefile(self.path, other.path)
        else:
            return False
    
    def __len__(self):
        # len(self)
        return len(self.contents)
    
    def __getitem__(self, key):
        # self[key]
        return self.contents[key]
    
    def __iter__(self):
        # iter(self)
        return iter(self.contents)
    
    def __reversed__(self):
        # reversed(self)
        return reversed(self.contents)
    
    def __contains__(self, item):
        # item in self
        return item in self.contents
    
    def isdir(self):
        # like os.path.isdir
        return self.basetype == 0
    
    def isfile(self):
        # like os.path.isfile
        return self.basetype == 1
    
    def basename(self):
        # like os.path.basename
        return self.name
    
    def dirname(self):
        # like os.path.dirname
        return self.location
    
    def join(self, *args):
        # like os.path.join
        return os.path.join(self.path, *args)
    
    def listdir(self):
        # like os.listdir
        if self.isdir():
            return self.contents
        else:
            err = OSError()
            err.errno = errno.ENOTDIR
            err.strerror = os.strerror(err.errno)
            err.filename = self.path
            raise err
    
    def samefile(self, other):
        # like os.path.samefile
        return os.path.samefile(self.path, other)
    
    def split(self):
        # like os.path.split
        return (self.location, self.name)
    
    def as_cell(self):
        # Create a ui.TableViewCell for use with FileDataSource
        cell = ui.TableViewCell()
        cell.text_label.text = self.name
        
        if self.basetype == 0:
            # is a folder
            cell.accessory_type = "detail_disclosure_button"
        else:
            # is a file
            cell.accessory_type = "detail_button"
        
        cell.image_view.image = FILE_ICONS[self.filetype]
        
        if self.filetype == "image":
            # attempt to generate a thumbnail
            try:
                thumb = PIL.Image.open(self.path)
                thumb.thumbnail((32, 32), PIL.Image.ANTIALIAS)
                #print(path + str(thmb.format))
                strio = StringIO.StringIO()
                thumb.save(strio, thumb.format)
                cell.image_view.image = ui.Image.from_data(strio.getvalue())
                strio.close()
            except IOError as err:
                pass
                #print(err)
        
        return cell

class FileDataSource(object):
    # ui.TableView data source that generates a directory listing
    def __init__(self, path=os.getcwd()):
        # init
        self.path = full_path(path)
        self.refresh()
        self.lists = [self.folders, self.files]

    def refresh(self):
        # Refresh the list of files and folders
        self.folders = []
        self.files = []
        for f in os.listdir(self.path):
            if os.path.isdir(os.path.join(self.path, f)):
                self.folders += f,
            else:
                self.files += f,

    def tableview_number_of_sections(self, tableview):
        # Return the number of sections
        return len(self.lists)

    def tableview_number_of_rows(self, tableview, section):
        # Return the number of rows in the section
        return len(self.lists[section])

    def tableview_cell_for_row(self, tableview, section, row):
        # Create and return a cell for the given section/row
        fi = FileItem(os.path.join(self.path, self.lists[section][row]))
        return fi.as_cell()
        """ # old code without FileItem
        cell = ui.TableViewCell()
        path = os.path.join(self.path, self.lists[section][row])
        name = os.path.basename(path)
        cell.text_label.text = name
        exts = name.rsplit(".") # the name itself is supposed to be kept, for detection of files like README
        if section == 0:
            cell.accessory_type = "detail_disclosure_button"
            cell.image_view.image = FILE_ICONS["folder"]
        elif section == 1:
            cell.accessory_type = "detail_button"
            cell.image_view.image = FILE_ICONS["file"]
        
        thumb_created = False
        for ext in exts:
            for type in FILE_TYPES:
                if ext.lower() in FILE_TYPES[type]:
                    cell.image_view.image = FILE_ICONS[type]
                    if type == "image" and not thumb_created:
                        # attempt to generate a thumbnail
                        try:
                            thumb_created = True
                            thmb = PIL.Image.open(path)
                            thmb.thumbnail((32, 32), PIL.Image.ANTIALIAS)
                            #print(path + str(thmb.format))
                            strio = StringIO.StringIO()
                            thmb.save(strio, thmb.format)
                            cell.image_view.image = ui.Image.from_data(strio.getvalue())
                            strio.close()
                        except IOError as err:
                            pass
                            #print(err)
        return cell
        #"""

    def tableview_title_for_header(self, tableview, section):
        # Return a title for the given section.
        if section == 0:
            return "Folders"
        elif section == 1:
            return "Files"
        else:
            return "errsec"

    def tableview_can_delete(self, tableview, section, row):
        # Return True if the user should be able to delete the given row.
        return False

    def tableview_can_move(self, tableview, section, row):
        # Return True if a reordering control should be shown for the given row (in editing mode).
        return False

    def tableview_delete(self, tableview, section, row):
        # Called when the user confirms deletion of the given row.
        pass

    def tableview_move_row(self, tableview, from_section, from_row, to_section, to_row):
        # Called when the user moves a row with the reordering control (in editing mode).
        pass
    
    def tableview_did_select(self, tableview, section, row):
        # Called when the user selects a row
        if not tableview.editing:
            if section == 0:
                nav.push_view(make_file_list(os.path.join(self.path, self.folders[row])))
            elif section == 1:
                open_path(os.path.join(self.path, self.files[row]))
                nav.close()
    
    def tableview_accessory_button_tapped(self, tableview, section, row):
        # Called when the user taps a row's accessory (i) button
        nav.push_view(make_stat_view(os.path.join(self.path, self.lists[section][row])))

class StatDataSource(object):
    # ui.TableView data source that shows os.stat() data on a file
    def __init__(self, path=os.getcwd()):
        # init
        self.path = full_path(path)
        self.refresh()
        self.lists = [self.actions, self.stats, self.flags]
        self.list_imgs = [self.action_imgs, self.stat_imgs, self.flag_imgs]

    def refresh(self):
        # Refresh stat data
        if os.path.isdir(self.path):
            self.type = 0
        else:
            self.type = 1
        self.actions = []
        self.action_imgs = []
        self.stats = []
        self.stat_imgs = []
        self.flags = []
        self.flag_imgs = []
        stres = os.stat(self.path)
        
        if self.type == 0:
            # actions for folders
            self.actions.append("Go here in Shellista")
            self.action_imgs.append(ui.Image.named("ionicons-ios7-arrow-forward-32"))
        elif self.type == 1:
            # actions for files
            self.actions.append("Quick Look")
            self.action_imgs.append(ui.Image.named("ionicons-ios7-eye-32"))
            self.actions.append("Open in Editor")
            self.action_imgs.append(ui.Image.named("ionicons-ios7-compose-32"))
            self.actions.append("Copy & Open")
            self.action_imgs.append(ui.Image.named("ionicons-ios7-copy-32"))
            self.actions.append("Copy & Open as Text")
            self.action_imgs.append(ui.Image.named("ionicons-document-text-32"))
            # haven't yet been able to integrate hexviewer
            #self.actions.append("Open in Hex Viewer")
            #self.action_imgs.append(ui.Image.named("ionicons-pound-32"))
            self.actions.append("Open in External App")
            self.action_imgs.append(ui.Image.named("ionicons-ios7-paperplane-32"))
        
        # general statistics
        self.stats.append("Size: " + str(stres.st_size) + " bytes")
        self.stat_imgs.append(ui.Image.named("ionicons-code-working-32"))
        self.stats.append("C: " + str(datetime.datetime.utcfromtimestamp(stres.st_ctime)) + " UTC")
        self.stat_imgs.append(ui.Image.named("ionicons-document-32"))
        self.stats.append("O: " + str(datetime.datetime.utcfromtimestamp(stres.st_atime)) + " UTC")
        self.stat_imgs.append(ui.Image.named("ionicons-folder-32"))
        self.stats.append("M: " + str(datetime.datetime.utcfromtimestamp(stres.st_mtime)) + " UTC")
        self.stat_imgs.append(ui.Image.named("ionicons-ios7-compose-32"))
        self.stats.append("Owner: " + str(stres.st_uid))
        self.stat_imgs.append(ui.Image.named("ionicons-ios7-person-32"))
        self.stats.append("Owner Group: " + str(stres.st_gid))
        self.stat_imgs.append(ui.Image.named("ionicons-ios7-people-32"))
        self.stats.append("Flags: " + str(bin(stres.st_mode)))
        self.stat_imgs.append(ui.Image.named("ionicons-ios7-flag-32"))
        
        flint = stres.st_mode
        
        self.flags.append("Is Socket: " + str(stat.S_ISSOCK(flint)))
        self.flags.append("Is Symlink: " + str(stat.S_ISLNK(flint)))
        self.flags.append("Is Regular File: " + str(stat.S_ISREG(flint)))
        self.flags.append("Is Block Device: " + str(stat.S_ISBLK(flint)))
        self.flags.append("Is Directory: " + str(stat.S_ISDIR(flint)))
        self.flags.append("Is Char Device: " + str(stat.S_ISCHR(flint)))
        self.flags.append("Is FIFO: " + str(stat.S_ISFIFO(flint)))
        self.flags.append("Set UID Bit: " + str(check_bit(flint, stat.S_ISUID)))
        self.flags.append("Set GID Bit: " + str(check_bit(flint, stat.S_ISGID)))
        self.flags.append("Sticky Bit: " + str(check_bit(flint, stat.S_ISVTX)))
        self.flags.append("May Owner Read: " + str(check_bit(flint, stat.S_IRUSR)))
        self.flags.append("May Owner Write: " + str(check_bit(flint, stat.S_IWUSR)))
        self.flags.append("May Owner Exec: " + str(check_bit(flint, stat.S_IXUSR)))
        self.flags.append("May Group Read: " + str(check_bit(flint, stat.S_IRGRP)))
        self.flags.append("May Group Write: " + str(check_bit(flint, stat.S_IWGRP)))
        self.flags.append("May Group Exec: " + str(check_bit(flint, stat.S_IXGRP)))
        self.flags.append("May Others Read: " + str(check_bit(flint, stat.S_IROTH)))
        self.flags.append("May Others Write: " + str(check_bit(flint, stat.S_IWOTH)))
        self.flags.append("May Others Exec: " + str(check_bit(flint, stat.S_IXOTH)))
        self.flag_imgs += [ui.Image.named("ionicons-ios7-flag-32")] * len(self.flags)
    
    def tableview_number_of_sections(self, tableview):
        # Return the number of sections
        return len(self.lists)

    def tableview_number_of_rows(self, tableview, section):
        # Return the number of rows in the section
        return len(self.lists[section])

    def tableview_cell_for_row(self, tableview, section, row):
        # Create and return a cell for the given section/row
        cell = ui.TableViewCell()
        cell.text_label.text = self.lists[section][row]
        cell.image_view.image = self.list_imgs[section][row]
        return cell

    def tableview_title_for_header(self, tableview, section):
        # Return a title for the given section.
        if section == 0:
            return "Actions"
        elif section == 1:
            return "Statistics"
        elif section == 2:
            return "Flags"
        else:
            return "errsec"

    def tableview_can_delete(self, tableview, section, row):
        # Return True if the user should be able to delete the given row.
        return False

    def tableview_can_move(self, tableview, section, row):
        # Return True if a reordering control should be shown for the given row (in editing mode).
        return False

    def tableview_delete(self, tableview, section, row):
        # Called when the user confirms deletion of the given row.
        pass

    def tableview_move_row(self, tableview, from_section, from_row, to_section, to_row):
        # Called when the user moves a row with the reordering control (in editing mode).
        pass
    
    @ui.in_background # necessary to avoid hangs with Shellista and console modules  
    def tableview_did_select(self, tableview, section, row):
        # Called when the user selects a row
        if section == 0:
            if self.type == 0:
                # actions for folders
                if row == 0:
                    # Go Here in Shellista
                    nav.close()
                    print("Launching Shellista...")
                    try:
                        from Shellista import Shell
                    except ImportError as err:
                        print("Failed to import Shellista: " + err.message)
                        print("See note on Shellista integration at the top of filenav.py.")
                        print("> logout")
                        return
                    shell = Shell()
                    shell.prompt = '> '
                    shell.onecmd("cd " + self.path)
                    print("> cd " + self.path)
                    shell.cmdloop()
            elif self.type == 1:
                # actions for files
                if row == 0:
                    # Quick Look
                    nav.close()
                    time.sleep(1) # ui thread will hang otherwise
                    console.quicklook(self.path)
                elif row == 1:
                    # Open in Editor
                    open_path(self.path)
                    nav.close()
                elif row == 2:
                    # Copy & Open
                    destdir = full_path(os.path.join(SCRIPT_ROOT, "temp"))
                    if not os.path.exists(destdir):
                        os.mkdir(destdir)
                    destfile = full_path(os.path.join(destdir, os.path.basename(self.path).lstrip(".")))
                    shutil.copy(self.path, destfile)
                    editor.reload_files()
                    open_path(destfile)
                    nav.close()
                elif row == 3:
                    # Copy & Open as Text
                    destdir = full_path(os.path.join(SCRIPT_ROOT, "temp"))
                    if not os.path.exists(destdir):
                        os.mkdir(destdir)
                    destfile = full_path(os.path.join(destdir, os.path.basename(self.path).lstrip(".") + ".txt"))
                    shutil.copy(self.path, destfile)
                    editor.reload_files()
                    open_path(destfile)
                    nav.close()
                elif row == 4:
                    # Open In
                    if console.open_in(self.path):
                        nav.close()
                    else:
                        console.hud_alert("Failed to Open", "error")
    
    def tableview_accessory_button_tapped(self, tableview, section, row):
        # Called when the user taps a row's accessory (i) button
        pass

def check_bit(num, bit):
    # Check if bit is set in num
    return (num ^ bit) < num

def open_path(path):
    # Open an absolute path in editor
    editor.open_file(os.path.relpath(path, os.path.expanduser("~/Documents")))

def toggle_edit_proxy(parent):
    # Returns a function that toggles edit mode for parent
    def _toggle_edit(sender):
        if parent.editing:
            sender.title = "Edit"
            parent.set_editing(False)
        else:
            sender.title = "Done"
            parent.set_editing(True)
    return _toggle_edit

def close_proxy():
    # Returns a function that closes the main view
    def _close(sender):
        nav.close()
        #wrap.close()
    return _close

def make_file_list(path):
    # Create a ui.TableView containing a directory listing of path
    path = full_path(path)
    ds = FileDataSource(path)
    lst = ui.TableView(flex="WH")
    # allow multiple selection when editing, single selection otherwise
    lst.allows_selection = True
    lst.allows_multiple_selection = False
    lst.allows_selection_during_editing = True
    lst.allows_multiple_selection_during_editing = True
    lst.background_color = 1.0
    lst.data_source = ds
    lst.delegate = ds
    lst.name = os.path.basename(path)
    lst.right_button_items = ui.ButtonItem(title="Edit", action=toggle_edit_proxy(lst)),
    current_list = lst
    return lst

def make_stat_view(path):
    # Create a ui.TableView containing stat data on path
    path = full_path(path)
    ds = StatDataSource(path)
    lst = ui.TableView(flex="WH")
    # allow single selection only outside edit mode
    lst.allows_selection = True
    lst.allows_multiple_selection = False
    lst.allows_selection_during_editing = False
    lst.allows_multiple_selection_during_editing = False
    lst.background_color = 1.0
    lst.data_source = ds
    lst.delegate = ds
    lst.name = os.path.basename(path)
    return lst

def run(path="~"):
    # Run the main UI application
    global lst
    global current_list
    global nav
    
    lst = make_file_list(path)
    lst.left_button_items = ui.ButtonItem(image=ui.Image.named("ionicons-close-24"), action=close_proxy()),
    
    current_list = lst

    nav = ui.NavigationView(lst)
    nav.navigation_bar_hidden = False
    nav.name = "FileNav"
    nav.flex = "WH"
    nav.height = 1000
    
    nav.present("popover", hide_title_bar=True)
    
    # attempt to fix spontaneous crashes when quitting from panel or sidebar
    # attempt failed, caused too many layout issues
    """
    nav.close()
    global wrap
    wrap = ui.View(name="FileNav", flex="WH")
    wrap.add_subview(nav)
    wrap.size_to_fit()
    
    #wrap.present("popover", hide_title_bar=True)
    """

if __name__ == "__main__":
    if len(sys.argv) > 1:
        run(str(sys.argv[1]))
    else:
        run("~")
