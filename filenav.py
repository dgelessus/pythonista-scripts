# -*- coding: utf-8 -*-
###############################################################################
# filenav by dgelessus
# http://github.com/dgelessus/pythonista-scripts/blob/master/filenav.py
###############################################################################

import datetime # used to format timestamps from os.stat()
import editor   # used to open files
import os       # used to navigate the file structure
import os.path  # ditto
import shutil   # used to copy files
import stat     # used to analyze stat results
import sys      # for sys.argv
import ui       # duh

SCRIPT_ROOT = os.path.split(sys.argv[0])[0]

def full_path(path):
    # Return absolute path with expanded ~s, input path assumed relative to cwd
    return os.path.abspath(os.path.join(os.getcwd(), os.path.expanduser(path)))

FILE_TYPES = {
              "app":       ("app", "exe", "nib", "pytheme", "pyui"),
              "archive":   ("bundle", "bz2", "cpgz", "gz", "gzip", "rar", "tar", "z", "zip"),
              "audio":     ("aac", "aif", "aiff", "caf", "m4a", "m4r", "mp3", "ogg", "wav"),
              "code":      ("c", "command", "cpp", "css", "h", "hpp", "js", "json", "makefile", "pxd", "pxi", "py", "pyc", "pyo", "pyx", "sh", "src"),
              "code_tags": ("htm", "html", "php", "plist", "xml"),
              "data":      ("bin", "dat"),
              "font":      ("fon", "otf", "ttf"),
              "image":     ("bmp", "gif", "icns", "itunesartwork", "jpg", "jpeg", "png"),
              "text":      ("authors", "build", "cfg", "changelog", "changes", "clslog", "contribs", "contributors", "copyright", "copyrights", "doc", "docx", "dot", "dotx", "ini", "install", "installation", "license", "md", "readme", "rtf", "txt", "version"),
              "video":     ("m4v", "mov", "mp4"),
              }

FILE_ICONS = {
              "app":       ui.Image.named(full_path("~/Pythonista.app/FileUI.png")),
              "archive":   ui.Image.named("ionicons-filing-32"),
              "audio":     ui.Image.named("ionicons-ios7-musical-notes-32"),
              "code":      ui.Image.named(full_path("~/Pythonista.app/FilePY.png")),
              "code_tags": ui.Image.named("ionicons-code-32"),
              "data":      ui.Image.named("ionicons-social-buffer-32"),
              "file":      ui.Image.named("ionicons-document-32"),
              #"folder":    ui.Image.named(full_path("~/Pythonista.app/Folder.png")),
              "folder":    ui.Image.named("ionicons-folder-32"),
              "font":      ui.Image.named(full_path("~/Pythonista.app/fonts-selected.png")),
              #"image":     ui.Image.named(full_path("~/Pythonista.app/FileImage.png")),
              "image":     ui.Image.named("ionicons-image-32"),
              #"text":      ui.Image.named(full_path("~/Pythonista.app/FileOther.png")),
              "text":      ui.Image.named("ionicons-document-text-32"),
              "video":     ui.Image.named("ionicons-ios7-film-outline-32"),
              }

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
        # indent this for loop to disable type-based icons for folders
        for ext in exts:
            for type in FILE_TYPES:
                if ext.lower() in FILE_TYPES[type]:
                    cell.image_view.image = FILE_ICONS[type]
        return cell

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
        self.actions = []
        self.action_imgs = []
        self.stats = []
        self.stat_imgs = []
        self.flags = []
        self.flag_imgs = []
        stres = os.stat(self.path)
        
        if os.path.isfile(self.path):
            self.actions.append("Open in Editor")
            self.action_imgs.append(ui.Image.named("ionicons-ios7-compose-32"))
            self.actions.append("Copy & Open")
            self.action_imgs.append(ui.Image.named("ionicons-ios7-copy-32"))
            self.actions.append("Copy & Open as Text")
            self.action_imgs.append(ui.Image.named("ionicons-document-text-32"))
        
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
    
    def tableview_did_select(self, tableview, section, row):
        # Called when the user selects a row
        if section == 0:
            if row == 0:
                open_path(self.path)
            elif row == 1:
                destdir = full_path(os.path.join(SCRIPT_ROOT, "temp"))
                if not os.path.exists(destdir):
                    os.mkdir(destdir)
                destfile = full_path(os.path.join(destdir, os.path.basename(self.path)))
                shutil.copy(self.path, destfile)
                editor.reload_files()
                open_path(destfile)
            elif row == 2:
                destdir = full_path(os.path.join(SCRIPT_ROOT, "temp"))
                if not os.path.exists(destdir):
                    os.mkdir(destdir)
                destfile = full_path(os.path.join(destdir, os.path.basename(self.path) + ".txt"))
                shutil.copy(self.path, destfile)
                editor.reload_files()
                open_path(destfile)
            nav.close()
    
    def tableview_accessory_button_tapped(self, tableview, section, row):
        # Called when the user taps a row's accessory (i) button
        pass

def check_bit(num, bit):
    return (num ^ bit) < num

def open_path(path):
    # Open an absolute path in editor
    editor.open_file(os.path.relpath(path, os.path.expanduser("~/Documents")))

def toggle_edit_proxy(parent):
    # returns a function that toggles edit mode for parent
    def _toggle_edit(sender):
        if parent.editing:
            sender.title = "Edit"
            parent.set_editing(False)
        else:
            sender.title = "Done"
            parent.set_editing(True)
    return _toggle_edit

def close_proxy():
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

if __name__ == "__main__":
    dlg = FileDataSource()

    lst = make_file_list("~")
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
    wrap = ui.View(name="FileNav", flex="WH")
    wrap.add_subview(nav)
    wrap.size_to_fit()
    
    #wrap.present("popover", hide_title_bar=True)
    """
