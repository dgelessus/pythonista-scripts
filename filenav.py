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
#import os.path   # ditto  # if you import os, you do not need to also import os.path
import PIL       # for thumbnail creation
import PIL.Image # ditto
import pwd       # to get names for UIDs
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

SCRIPT_ROOT = full_path("~") if sys.argv[0] == "prompt" else os.path.dirname(sys.argv[0])

# list of file size units
SIZE_SUFFIXES = "bytes KiB MiB GiB TiB PiB EiB ZiB YiB".split()

# dict of known file extensions
FILE_EXTS = {
             "aac":  "Apple Audio",
             "aif":  "AIFF Audio",
             "aiff": "AIFF Audio",
             "app":  "Mac or iOS App Bundle",
             "authors": "Author List",
             "avi":  "AVI Video",
             "bin":  "Binary Data",
             "bmp":  "Microsoft Bitmap Image",
             "build": "Build Instructions",
             "bundle": "Bundle",
             "bz2":  "Bzip2 Archive",
             "c":    "C Source Code",
             "cache": "Data Cache",
             "caf":  "CAF Audio",
             "cfg":  "Configuration File",
             "changelog": "Changelog",
             "changes": "Changelog",
             "command": "Shell Script",
             "conf": "Configuration File",
             "contribs": "Contributor List",
             "contributors": "Contributor List",
             "copyright": "Copyright Notice",
             "copyrights": "Copyright Notice",
             "cpgz": "CPGZ Archive",
             "cpp":  "C++ Source Code",
             "css":  "Cascading Style Sheet",
             "csv":  "Comma-separated Values",
             "dat":  "Data",
             "db":   "Database",
             "dmg":  "Mac Disk Image",
             "doc":  "MS Word Document",
             "docx": "MS Word Document (XML-based)",
             "dot":  "MS Word Template",
             "dotx": "MS Word Template (XML-based)",
             "exe":  "Windows Executable",
             "fon":  "Bitmap Font",
             "gif":  "GIF Image",
             "git":  "Git Data",
             "gitignore": "Git File Ignore List",
             "gz":   "Gzip Archive",
             "gzip": "Gzip Archive",
             "h":    "C Header Source Code",
             "hgignore": "Mercurial File Ignore List",
             "hgsubstate": "Mercurial Substate",
             "hgtags": "Mercurial Tags",
             "hpp":  "C++ Header Source Code",
             "htm":  "HTML File",
             "html": "HTML File",
             "icns": "Apple Icon Image",
             "in":   "Configuration File",
             "ini":  "MS INI File",
             "install": "Install Instructions",
             "installation": "Install Instructions",
             "itunesartwork": "iOS App Logo",
             "jpg":  "JPEG Image",
             "jpeg": "JPEG Image",
             "js":   "JavaScript",
             "json": "JSON File",
             "license": "License",
             "m4a":  "MPEG-4 Audio",
             "m4r":  "MPEG-4 Ringtone",
             "m4v":  "MPEG-4 Video",
             "makefile": "Makefile",
             "md":   "Markdown Text",
             "mov":  "Apple MOV Video",
             "mp3":  "MPEG-3 Audio",
             "mp4":  "MPEG-4 Video",
             "nib":  "Mac or iOS Interface File",
             "odf":  "ODF Document",
             "odp":  "ODF Slideshow",
             "ods":  "ODF Spreadsheet",
             "odt":  "ODF Text",
             "ogg":  "Ogg Vorbis Audio",
             "otf":  "OpenType Font",
             "pages": "Apple Pages Document",
             "pdf":  "PDF Document",
             "php":  "PHP Script",
             "pkl":  "Python Pickle Data",
             "plist": "Apple Property List",
             "png":  "PNG Image",
             "pps":  "MS PowerPoint Template",
             "ppsx": "MS PowerPoint Template (XML-based)",
             "ppt":  "MS PowerPoint Slideshow",
             "pptx": "MS PowerPoint Slideshow (XML-based)",
             "pxd":  "Pyrex Script",
             "pxi":  "Pyrex Script",
             "py":   "Python Script",
             "pyc":  "Python Bytecode",
             "pyo":  "Python Bytecode",
             "pyx":  "Pyrex Script",
             "pytheme": "Pythonista Code Theme",
             "pyui": "Pythonista UI File",
             "rar":  "RAR Archive",
             "readme": "Read Me File",
             "rst":  "reStructured Text",
             "rtf":  "RTF Document",
             "sh":   "Shell Script",
             "src":  "Source Code",
             "svg":  "Scalable Vector Graphic",
             "tar":  "Tar Archive",
             "tgz":  "Tar Ball",
             "ttc":  "TrueType Font Collection",
             "ttf":  "TrueType Font",
             "txt":  "Plain Text",
             "version": "Version Details",
             "xls":  "MS Excel Spreadsheet",
             "xlsx": "MS Excel Spreadsheet (XML-based)",
             "xlt":  "MS Excel Template",
             "xltx": "MS Excel Template (XML-based)",
             "xml":  "XML File",
             "yml":  "YML File",
             "wav":  "Waveform Audio",
             "z":    "Compressed Archive",
             "zip":  "Zip Archive",
             }

# dict of known file type groups and extensions
FILE_TYPES = {
    "app":       "app exe nib pytheme pyui",
    "archive":   "bundle bz2 cpgz dmg gz gzip rar tar tgz z zip",
    "audio":     "aac aif aiff caf m4a m4r mp3 ogg wav",
    "code":      """c command cpp css h hpp js json makefile pxd pxi py pyx
                    sh src""",
    "code_tags": "htm html php plist xml",
    "data":      "bin cache dat db pkl pyc pyo",
    "font":      "fon otf ttc ttf",
    "git":       "git gitignore",
    "image":     "bmp gif icns itunesartwork jpg jpeg png svg",
    "text":      """authors build cfg changelog changes clslog conf contribs
                    contributors copyright copyrights csv doc docx dot dotx
                    hgignore hgsubstate hgtags in ini install installation
                    license md odf odp ods odt pages pdf pps ppsx ppt pptx
                    readme rst rtf txt version xls xlsx xlt xltx yml""",
    "video":     "avi m4v mov mp4"
              }
FILE_TYPES = {k:tuple(v.split()) for k,v in FILE_TYPES.iteritems()}

# dict of descriptions for all file type groups
FILE_DESCS = {
              "app":       "Application",
              "archive":   "Archive",
              "audio":     "Audio File",
              "code":      "Source Code",
              "code_tags": "Source Code",
              "data":      "Data File",
              "file":      "File",
              "folder":    "Folder",
              "font":      "Font File",
              "git":       None,
              "image":     "Image File",
              "text":      "Plain Text File",
              "video":     "Video File",
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

def get_thumbnail(path):
    # attempt to generate a thumbnail
    try:
        thumb = PIL.Image.open(path)
        thumb.thumbnail((32, 32), PIL.Image.ANTIALIAS)
        #print(path + str(thumb.format))
        strio = StringIO.StringIO()
        thumb.save(strio, thumb.format)
        data = strio.getvalue()
        strio.close()
        return ui.Image.from_data(data)
    except IOError as err:
        if err.message == "broken data stream when reading image file":
            # load image using ui module first
            with open(os.path.join(SCRIPT_ROOT, "temp/filenav-tmp.png"), "wb") as f:
                f.write(ui.Image.named(path).to_png())
            # need to close and reopen file, otherwise PIL fails to read the image
            with open(os.path.join(SCRIPT_ROOT, "temp/filenav-tmp.png"), "rb") as f:
                thumb = PIL.Image.open(f)
                thumb.thumbnail((32, 32), PIL.Image.ANTIALIAS)
                #print(path + str(thumb.format))
                strio = StringIO.StringIO()
                thumb.save(strio, thumb.format)
            data = strio.getvalue()
            strio.close()
            return ui.Image.from_data(data)
        return None
        #print(err)

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
        try:
            self.stat = os.stat(self.path)
        except OSError as err:
            self.stat = err
        
        if os.path.isdir(self.path):
            self.basetype = 0
            self.filetype = "folder"
            try:
                self.contents = os.listdir(self.path)
            except OSError as err:
                self.contents = err
        else:
            self.basetype = 1
            self.filetype = "file"
            self.contents = []
        
        for part in self.nameparts:
            for type in FILE_TYPES:
                if part.lower() in FILE_TYPES[type]:
                    self.filetype = type
        
        self.icon = None
    
    def __del__(self):
        #print("uncaching " + self.path)
        del self.path
        del self.rel_to_docs
        del self.location
        del self.name
        del self.nameparts
        del self.stat
        del self.basetype
        del self.filetype
        del self.contents
        del self.icon
    
    def __repr__(self):
        # repr(self) and str(self)
        return "filenav.FileItem(" + self.path + ")"
    
    def __eq__(self, other):
        # self == other
        return os.path.samefile(self.path, other.path) if isinstance(other, FileItem) else False

    def __ne__(self, other):
        # self != other
        return not os.path.samefile(self.path, other.path) if isinstance(other, FileItem) else False
    
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
        cell = ui.TableViewCell("subtitle")
        cell.text_label.text = self.name
        
        if self.basetype == 0:
            # is a folder
            cell.accessory_type = "detail_disclosure_button"
            cell.detail_text_label.text = "Folder"
            
            # only apply certain descriptions to folders
            if self.filetype in ("app", "bundle", "git"):
                try:
                    cell.detail_text_label.text = FILE_EXTS[self.nameparts[len(self.nameparts)-1].lower()]
                except KeyError:
                    try:
                        cell.detail_text_label.text = FILE_DESCS[self.filetype]
                    except KeyError:
                        pass
            
            if not self.icon:
                cell.image_view.image = FILE_ICONS["folder"]
                # only apply certain icons to folders
                if self.filetype in ("app", "archive", "bundle", "git"):
                    cell.image_view.image = FILE_ICONS[self.filetype]
            
        else:
            # is a file
            cell.accessory_type = "detail_button"
            cell.detail_text_label.text = "File"
            
            try:
                cell.detail_text_label.text = FILE_EXTS[self.nameparts[len(self.nameparts)-1].lower()]
            except KeyError:
                try:
                    cell.detail_text_label.text = FILE_DESCS[self.filetype]
                except KeyError:
                    pass
            
            if not self.icon:
                cell.image_view.image = FILE_ICONS[self.filetype]
                if self.filetype == "image":
                    thumb = get_thumbnail(self.path)
                    if thumb:
                        cell.image_view.image = thumb
        
        if self.icon:
            cell.image_view.image = self.icon
        else:
            self.icon = cell.image_view.image
        
        # add size to subtitle
        if not isinstance(self.stat, OSError):
            cell.detail_text_label.text += " (" + format_size(self.stat.st_size, False) + ")"
        
        return cell

CWD_FILE_ITEM = FileItem(os.getcwd())

class FileDataSource(object):
    # ui.TableView data source that generates a directory listing
    def __init__(self, fi=CWD_FILE_ITEM):
        # init
        self.fi = fi
        self.refresh()
        self.lists = [self.folders, self.files]

    def refresh(self):
        # Refresh the list of files and folders
        self.folders = []
        self.files = []
        for i in range(len(self.fi.contents)):
            if not isinstance(self.fi.contents[i], FileItem):
                # if it isn't already, make entries FileItems rather than strings
                self.fi.contents[i] = FileItem(self.fi.join(self.fi.contents[i]))
            
            if self.fi.contents[i].isdir():
                self.folders.append(self.fi.contents[i])
            else:
                self.files.append(self.fi.contents[i])

    def tableview_number_of_sections(self, tableview):
        # Return the number of sections
        return len(self.lists)

    def tableview_number_of_rows(self, tableview, section):
        # Return the number of rows in the section
        return len(self.lists[section])

    def tableview_cell_for_row(self, tableview, section, row):
        # Create and return a cell for the given section/row
        return self.lists[section][row].as_cell()

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
                nav.push_view(make_file_list(self.lists[section][row]))
            elif section == 1:
                open_path(self.lists[section][row].path)
                nav.close()
    
    def tableview_accessory_button_tapped(self, tableview, section, row):
        # Called when the user taps a row's accessory (i) button
        nav.push_view(make_stat_view(self.lists[section][row]))

class StatDataSource(object):
    # ui.TableView data source that shows os.stat() data on a file
    def __init__(self, fi=CWD_FILE_ITEM):
        # init
        self.fi = fi
        self.refresh()
        self.lists = [self.actions, self.stats, self.flags]
        self.list_details = [self.action_details, self.stat_details, self.flag_details]
        self.list_imgs = [self.action_imgs, self.stat_imgs, self.flag_imgs]

    def refresh(self):
        # Refresh stat data
        self.actions = []
        self.action_details = []
        self.action_imgs = []
        self.stats = []
        self.stat_details = []
        self.stat_imgs = []
        self.flags = []
        self.flag_details = []
        self.flag_imgs = []
        stres = self.fi.stat
        
        if self.fi.isdir():
            # actions for folders
            self.actions.append("Go here")
            self.action_details.append("Shellista")
            self.action_imgs.append(ui.Image.named("ionicons-ios7-arrow-forward-32"))
        elif self.fi.isfile():
            # actions for files
            self.actions.append("Preview")
            self.action_details.append("Quick Look")
            self.action_imgs.append(ui.Image.named("ionicons-ios7-eye-32"))
            self.actions.append("Open in Editor")
            self.action_details.append("Pythonista")
            self.action_imgs.append(ui.Image.named("ionicons-ios7-compose-32"))
            self.actions.append("Copy & Open")
            self.action_details.append("Pythonista")
            self.action_imgs.append(ui.Image.named("ionicons-ios7-copy-32"))
            self.actions.append("Copy & Open as Text")
            self.action_details.append("Pythonista")
            self.action_imgs.append(ui.Image.named("ionicons-document-text-32"))
            # haven't yet been able to integrate hexviewer
            #self.actions.append("Open in Hex Viewer")
            #self.action_details.append("hexviewer")
            #self.action_imgs.append(ui.Image.named("ionicons-pound-32"))
            self.actions.append("Open in and Share")
            self.action_details.append("External Apps")
            self.action_imgs.append(ui.Image.named("ionicons-ios7-paperplane-32"))
        
        # general statistics
        self.stats.append("Size")
        self.stat_details.append(format_size(stres.st_size))
        self.stat_imgs.append(ui.Image.named("ionicons-code-working-32"))
        self.stats.append("Created")
        self.stat_details.append(str(datetime.datetime.utcfromtimestamp(stres.st_ctime)) + " UTC")
        self.stat_imgs.append(ui.Image.named("ionicons-document-32"))
        self.stats.append("Opened")
        self.stat_details.append(str(datetime.datetime.utcfromtimestamp(stres.st_atime)) + " UTC")
        self.stat_imgs.append(ui.Image.named("ionicons-folder-32"))
        self.stats.append("Modified")
        self.stat_details.append(str(datetime.datetime.utcfromtimestamp(stres.st_mtime)) + " UTC")
        self.stat_imgs.append(ui.Image.named("ionicons-ios7-compose-32"))
        self.stats.append("Owner")
        self.stat_details.append("{udesc} ({uid}={uname})".format(uid=stres.st_uid, uname=pwd.getpwuid(stres.st_uid)[0], udesc=pwd.getpwuid(stres.st_uid)[4]))
        self.stat_imgs.append(ui.Image.named("ionicons-ios7-person-32"))
        self.stats.append("Owner Group")
        self.stat_details.append(str(stres.st_gid))
        self.stat_imgs.append(ui.Image.named("ionicons-ios7-people-32"))
        self.stats.append("Flags")
        self.stat_details.append(str(bin(stres.st_mode)))
        self.stat_imgs.append(ui.Image.named("ionicons-ios7-flag-32"))
        #self.stat_details += ["Detail"] * len(self.stats)
        
        flint = stres.st_mode
        
        self.flags.append("Is Socket")
        self.flag_details.append(str(stat.S_ISSOCK(flint)))
        self.flags.append("Is Symlink")
        self.flag_details.append(str(stat.S_ISLNK(flint)))
        self.flags.append("Is File")
        self.flag_details.append(str(stat.S_ISREG(flint)))
        self.flags.append("Is Block Dev.")
        self.flag_details.append(str(stat.S_ISBLK(flint)))
        self.flags.append("Is Directory")
        self.flag_details.append(str(stat.S_ISDIR(flint)))
        self.flags.append("Is Char Dev.")
        self.flag_details.append(str(stat.S_ISCHR(flint)))
        self.flags.append("Is FIFO")
        self.flag_details.append(str(stat.S_ISFIFO(flint)))
        self.flags.append("Set UID Bit")
        self.flag_details.append(str(check_bit(flint, stat.S_ISUID)))
        self.flags.append("Set GID Bit")
        self.flag_details.append(str(check_bit(flint, stat.S_ISGID)))
        self.flags.append("Sticky Bit")
        self.flag_details.append(str(check_bit(flint, stat.S_ISVTX)))
        self.flags.append("Owner Read")
        self.flag_details.append(str(check_bit(flint, stat.S_IRUSR)))
        self.flags.append("Owner Write")
        self.flag_details.append(str(check_bit(flint, stat.S_IWUSR)))
        self.flags.append("Owner Exec")
        self.flag_details.append(str(check_bit(flint, stat.S_IXUSR)))
        self.flags.append("Group Read")
        self.flag_details.append(str(check_bit(flint, stat.S_IRGRP)))
        self.flags.append("Group Write")
        self.flag_details.append(str(check_bit(flint, stat.S_IWGRP)))
        self.flags.append("Group Exec")
        self.flag_details.append(str(check_bit(flint, stat.S_IXGRP)))
        self.flags.append("Others Read")
        self.flag_details.append(str(check_bit(flint, stat.S_IROTH)))
        self.flags.append("Others Write")
        self.flag_details.append(str(check_bit(flint, stat.S_IWOTH)))
        self.flags.append("Others Exec")
        self.flag_details.append(str(check_bit(flint, stat.S_IXOTH)))
        #self.flag_details += ["Detail"] * len(self.flags)
        self.flag_imgs += [ui.Image.named("ionicons-ios7-flag-32")] * len(self.flags)
    
    def tableview_number_of_sections(self, tableview):
        # Return the number of sections
        return len(self.lists)

    def tableview_number_of_rows(self, tableview, section):
        # Return the number of rows in the section
        return len(self.lists[section])

    def tableview_cell_for_row(self, tableview, section, row):
        # Create and return a cell for the given section/row
        if section == 0:
            cell = ui.TableViewCell("subtitle")
            cell.image_view.image = self.list_imgs[section][row]
        else:
            cell = ui.TableViewCell("value2")
        cell.text_label.text = self.lists[section][row]
        cell.detail_text_label.text = self.list_details[section][row]
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
            if self.fi.isdir():
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
                    shell.onecmd("cd " + self.fi.path)
                    print("> cd " + self.fi.path)
                    shell.cmdloop()
            elif self.fi.isfile():
                # actions for files
                if row == 0:
                    # Quick Look
                    nav.close()
                    time.sleep(1) # ui thread will hang otherwise
                    console.quicklook(self.fi.path)
                elif row == 1:
                    # Open in Editor
                    open_path(self.fi.path)
                    nav.close()
                elif row == 2:
                    # Copy & Open
                    destdir = full_path(os.path.join(SCRIPT_ROOT, "temp"))
                    if not os.path.exists(destdir):
                        os.mkdir(destdir)
                    destfile = full_path(os.path.join(destdir, self.fi.basename().lstrip(".")))
                    shutil.copy(self.path, destfile)
                    editor.reload_files()
                    open_path(destfile)
                    nav.close()
                elif row == 3:
                    # Copy & Open as Text
                    destdir = full_path(os.path.join(SCRIPT_ROOT, "temp"))
                    if not os.path.exists(destdir):
                        os.mkdir(destdir)
                    destfile = full_path(os.path.join(destdir, self.fi.basename().lstrip(".") + ".txt"))
                    shutil.copy(self.path, destfile)
                    editor.reload_files()
                    open_path(destfile)
                    nav.close()
                elif row == 4:
                    # Open In
                    if console.open_in(self.fi.path):
                        nav.close()
                    else:
                        console.hud_alert("Failed to Open", "error")
    
    def tableview_accessory_button_tapped(self, tableview, section, row):
        # Called when the user taps a row's accessory (i) button
        pass

def check_bit(num, bit):
    # Check if bit is set in num
    return (num ^ bit) < num

def format_size(size, long=True):
    if size < 1024:
        return str(int(size)) + " bytes"
    else:
        size, bsize = float(size), int(size)
        i = 0
        while size >= 1024.0 and i < len(SIZE_SUFFIXES)-1:
            size = size/1024.0
            i += 1
        if long:
            return "{size:02.2f} {suffix} ({bsize} bytes)".format(size=size, suffix=SIZE_SUFFIXES[i], bsize=bsize)
        else:
            return "{size:01.1f} {suffix}".format(size=size, suffix=SIZE_SUFFIXES[i])

def open_path(path):
    # Open an absolute path in editor
    editor.open_file(os.path.relpath(path, os.path.expanduser("~/Documents")))

def toggle_edit_proxy(parent):
    # Returns a function that toggles edit mode for parent
    def _toggle_edit(sender):
        sender.title = "Edit" if parent.editing else "Done"
        parent.set_editing(not parent.editing)
    return _toggle_edit

def close_proxy():
    # Returns a function that closes the main view
    def _close(sender):
        nav.close()
        #wrap.close()
    return _close

def make_file_list(fi=CWD_FILE_ITEM):
    # Create a ui.TableView containing a directory listing of path
    ds = FileDataSource(fi)
    lst = ui.TableView(flex="WH")
    # allow multiple selection when editing, single selection otherwise
    lst.allows_selection = True
    lst.allows_multiple_selection = False
    lst.allows_selection_during_editing = True
    lst.allows_multiple_selection_during_editing = True
    lst.background_color = 1.0
    lst.data_source = lst.delegate = ds
    
    lst.name = "/" if fi.path == "/" else fi.basename()
    lst.right_button_items = ui.ButtonItem(title="Edit", action=toggle_edit_proxy(lst)),
    return lst

def make_stat_view(fi=CWD_FILE_ITEM):
    # Create a ui.TableView containing stat data on path
    ds = StatDataSource(fi)
    lst = ui.TableView(flex="WH")
    # allow single selection only outside edit mode
    lst.allows_selection = True
    lst.allows_multiple_selection = False
    lst.allows_selection_during_editing = False
    lst.allows_multiple_selection_during_editing = False
    lst.background_color = 1.0
    lst.data_source = lst.delegate = ds
    lst.name = "/" if fi.path == "/" else fi.basename()
    return lst

def run(path="~"):
    # Run the main UI application
    global nav
    
    lst = make_file_list(CWD_FILE_ITEM if full_path(path) == "~" else FileItem(path))
    lst.left_button_items = ui.ButtonItem(image=ui.Image.named("ionicons-close-24"),
                                          action=close_proxy()),
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
    run(sys.argv[1] if len(sys.argv) > 1 else "~")
