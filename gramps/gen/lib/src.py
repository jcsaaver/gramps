#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2007  Donald N. Allingham
# Copyright (C) 2010       Michiel D. Nauta
# Copyright (C) 2011       Tim G L Lyons
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#

# $Id$

"""
Source object for GRAMPS.
"""

#-------------------------------------------------------------------------
#
# GRAMPS modules
#
#-------------------------------------------------------------------------
from .primaryobj import PrimaryObject
from .mediabase import MediaBase
from .notebase import NoteBase
from .tagbase import TagBase
from .srcattrbase import SrcAttributeBase
from .srctemplate import SrcTemplate
from .reporef import RepoRef
from .const import DIFFERENT, EQUAL, IDENTICAL
from ..constfunc import cuni, deprecated
from .handle import Handle

#-------------------------------------------------------------------------
#
# Source class
#
#-------------------------------------------------------------------------
class Source(MediaBase, NoteBase, SrcAttributeBase, PrimaryObject):
    """A record of a source of information."""
    
    def __init__(self):
        """Create a new Source instance."""
        PrimaryObject.__init__(self)
        MediaBase.__init__(self)
        NoteBase.__init__(self)
        SrcAttributeBase.__init__(self)
        self.name = ""
        self.template = 'GEDCOM'
        self.abbrev = ""
        self.reporef_list = []
        
    def serialize(self):
        """
        Convert the object to a serialized tuple of data.
        """
        return (self.handle,                                       # 0
                self.gramps_id,                                    # 1
                cuni(self.name),                                   # 2
                cuni(self.template),                               # 3
                NoteBase.serialize(self),                          # 4
                MediaBase.serialize(self),                         # 5
                cuni(self.abbrev),                                 # 6
                self.change,                                       # 7
                SrcAttributeBase.serialize(self),                  # 8
                [rr.serialize() for rr in self.reporef_list],      # 9
                TagBase.serialize(self),                           # 10
                self.private)                                      # 11

    def to_struct(self):
        """
        Convert the data held in this object to a structure (eg,
        struct) that represents all the data elements.
        
        This method is used to recursively convert the object into a
        self-documenting form that can easily be used for various
        purposes, including diffs and queries.

        These structures may be primitive Python types (string,
        integer, boolean, etc.) or complex Python types (lists,
        tuples, or dicts). If the return type is a dict, then the keys
        of the dict match the fieldname of the object. If the return
        struct (or value of a dict key) is a list, then it is a list
        of structs. Otherwise, the struct is just the value of the
        attribute.

        :returns: Returns a struct containing the data of the object.
        :rtype: dict
        """
        return {"handle": Handle("Source", self.handle), 
                "gramps_id": self.gramps_id, 
                "name": cuni(self.name),
                "template": cuni(self.template),
                "note_list": NoteBase.to_struct(self),
                "media_list": MediaBase.to_struct(self), 
                "abbrev": cuni(self.abbrev),
                "change": self.change,
                "srcattr_list": SrcAttributeBase.to_struct(self),
                "reporef_list": [rr.to_struct() for rr in self.reporef_list],
                "tag_list": TagBase.to_struct(self),
                "private": self.private}

    def unserialize(self, data):
        """
        Convert the data held in a tuple created by the serialize method
        back into the data in an Event structure.
        """
        (self.handle,       #  0
         self.gramps_id,    #  1
         self.name,         #  2
         self.template,     #  3
         note_list,         #  4
         media_list,        #  5
         self.abbrev,       #  6
         self.change,       #  7
         srcattr_list,      #  8
         reporef_list,      #  9
         tag_list,          #  10
         self.private       #  11
        ) = data

        NoteBase.unserialize(self, note_list)
        MediaBase.unserialize(self, media_list)
        TagBase.unserialize(self, tag_list)
        SrcAttributeBase.unserialize(self, srcattr_list)
        self.reporef_list = [RepoRef().unserialize(item) for item in reporef_list]
        return self
        
    def _has_handle_reference(self, classname, handle):
        """
        Return True if the object has reference to a given handle of given 
        primary object type.
        
        :param classname: The name of the primary object class.
        :type classname: str
        :param handle: The handle to be checked.
        :type handle: str
        :returns: Returns whether the object has reference to this handle of 
                this object type.
        :rtype: bool
        """
        if classname == 'Repository':
            return handle in [ref.ref for ref in self.reporef_list]
        return False

    def _remove_handle_references(self, classname, handle_list):
        """
        Remove all references in this object to object handles in the list.

        :param classname: The name of the primary object class.
        :type classname: str
        :param handle_list: The list of handles to be removed.
        :type handle_list: str
        """
        if classname == 'Repository':
            new_list = [ref for ref in self.reporef_list
                            if ref.ref not in handle_list]
            self.reporef_list = new_list

    def _replace_handle_reference(self, classname, old_handle, new_handle):
        """
        Replace all references to old handle with those to the new handle.

        :param classname: The name of the primary object class.
        :type classname: str
        :param old_handle: The handle to be replaced.
        :type old_handle: str
        :param new_handle: The handle to replace the old one with.
        :type new_handle: str
        """
        if classname == 'Repository':
            handle_list = [ref.ref for ref in self.reporef_list]
            while old_handle in handle_list:
                idx = handle_list.index(old_handle)
                self.reporef_list[idx].ref = new_handle
                handle_list[idx] = ''

    def get_text_data_list(self):
        """
        Return the list of all textual attributes of the object.

        :returns: Returns the list of all textual attributes of the object.
        :rtype: list
        """
        return [self.title, self.author, self.pubinfo, self.abbrev,
                self.gramps_id]
    
    def get_text_data_child_list(self):
        """
        Return the list of child objects that may carry textual data.

        :returns: Returns the list of child objects that may carry textual data.
        :rtype: list
        """
        return self.media_list + self.reporef_list + self.attribute_list

    def get_citation_child_list(self):
        """
        Return the list of child secondary objects that may refer citations.

        :returns: Returns the list of child secondary child objects that may 
                refer citations.
        :rtype: list
        """
        return self.media_list

    def get_note_child_list(self):
        """
        Return the list of child secondary objects that may refer notes.

        :returns: Returns the list of child secondary child objects that may 
                refer notes.
        :rtype: list
        """
        return self.media_list + self.reporef_list

    def get_handle_referents(self):
        """
        Return the list of child objects which may, directly or through
        their children, reference primary objects.
        
        :returns: Returns the list of objects referencing primary objects.
        :rtype: list
        """
        return self.get_citation_child_list() + self.reporef_list

    def get_referenced_handles(self):
        """
        Return the list of (classname, handle) tuples for all directly
        referenced primary objects.
        
        :returns: List of (classname, handle) tuples for referenced objects.
        :rtype: list
        """
        return (self.get_referenced_note_handles() +
                self.get_referenced_tag_handles())

    def merge(self, acquisition):
        """
        Merge the content of acquisition into this source.

        :param acquisition: The source to merge with the present source.
        :rtype acquisition: Source
        """
        self._merge_privacy(acquisition)
        self._merge_note_list(acquisition)
        self._merge_media_list(acquisition)
        self._merge_tag_list(acquisition)
        self._merge_attribute_list(acquisition)
        self._merge_reporef_list(acquisition)

    def set_template(self, template):
        """
        Set the template type of the Source object. This defines a number of
        preset SrcAttributes to be filled in by the user
        
        :param template: a template code as defined in SrcTemplate
        :type template: str
        """
        self.template = template

    def get_template(self):
        """Return the template type of the Source
        
        :returns: Returns the code of the SrcTemplate set for this Source
        :rtype: str
        """
        return self.template

    def set_name(self, name):
        """
        Set a descriptive name for the Source object, which will be used in 
        Gramps for sorting, identification.
        Typically, this value is set automatically based on the template, but
        is user changeable if needed.
        
        :param name: a descriptive name to assign to the Source
        :type name: str
        """
        self.name = name

    def get_name(self):
        """
        Return the descriptive name of the source

        :returns: Returns the descriptive name of the source
        :rtype: str
        """
        return self.name

    def set_abbreviation(self, abbrev):
        """Set the title abbreviation of the Source used for LOCAL 
           sorting or filing.
        
        :param abbrev: Short form used to retrieve Source locally
        :type abbrev: str
        """
        self.abbrev = abbrev

    def get_abbreviation(self):
        """Return the title abbreviation of the Source used for LOCAL 
           sorting or filing.
        
        :returns: Short form used to retrieve Source locally
        :rtype: str
        """
        return self.abbrev

    def add_repo_reference(self, repo_ref):
        """
        Add a :class:`~gen.lib.reporef,RepoRef` instance to the Source's reporef list.

        :param repo_ref: :class:`~gen.lib.reporef,RepoRef` instance to be added to the object's 
                reporef list.
        :type repo_ref: :class:`~gen.lib.reporef,RepoRef`
        """
        self.reporef_list.append(repo_ref)

    def get_reporef_list(self):
        """
        Return the list of :class:`~gen.lib.reporef,RepoRef` instances associated with the Source.

        @Return: list of :class:`~gen.lib.reporef,RepoRef` instances associated with the Source
        :rtype: list
        """
        return self.reporef_list

    def set_reporef_list(self, reporef_list):
        """
        Set the list of :class:`~gen.lib.reporef,RepoRef` instances associated with the Source.
        It replaces the previous list.

        :param reporef_list: list of :class:`~gen.lib.reporef,RepoRef` instances to be assigned to 
                the Source.
        :type reporef_list: list
        """
        self.reporef_list = reporef_list

    def _merge_reporef_list(self, acquisition):
        """
        Merge the list of repository references from acquisition with our own.

        :param acquisition: the repository references list of this object will
            be merged with the current repository references list.
        :rtype acquisition: RepoRef
        """
        reporef_list = self.reporef_list[:]
        for addendum in acquisition.get_reporef_list():
            for reporef in reporef_list:
                equi = reporef.is_equivalent(addendum)
                if equi == IDENTICAL:
                    break
                elif equi == EQUAL:
                    reporef.merge(addendum)
                    break
            else:
                self.reporef_list.append(addendum)

    def has_repo_reference(self, repo_handle):
        """
        Return True if the Source has reference to this Repository handle.

        :param repo_handle: The Repository handle to be checked.
        :type repo_handle: str
        :returns: Returns whether the Source has reference to this Repository 
                handle.
        :rtype: bool
        """
        return repo_handle in [repo_ref.ref for repo_ref in self.reporef_list]

    def remove_repo_references(self, repo_handle_list):
        """
        Remove references to all Repository handles in the list.

        :param repo_handle_list: The list of Repository handles to be removed.
        :type repo_handle_list: list
        """
        new_reporef_list = [repo_ref for repo_ref in self.reporef_list
                                if repo_ref.ref not in repo_handle_list]
        self.reporef_list = new_reporef_list

    def replace_repo_references(self, old_handle, new_handle):
        """
        Replace all references to old Repository handle with the new handle
        and merge equivalent entries.

        :param old_handle: The Repository handle to be replaced.
        :type old_handle: str
        :param new_handle: The Repository handle to replace the old one with.
        :type new_handle: str
        indikken
        """
        refs_list = [ repo_ref.ref for repo_ref in self.reporef_list ]
        new_ref = None
        if new_handle in refs_list:
            new_ref = self.reporef_list[refs_list.index(new_handle)]
        n_replace = refs_list.count(old_handle)
        for ix_replace in range(n_replace):
            idx = refs_list.index(old_handle)
            self.reporef_list[idx].ref = new_handle
            refs_list[idx] = new_handle
            if new_ref:
                repo_ref = self.reporef_list[idx]
                equi = new_ref.is_equivalent(repo_ref)
                if equi != DIFFERENT:
                    if equi == EQUAL:
                        new_ref.merge(repo_ref)
                    self.reporef_list.pop(idx)
                    refs_list.pop(idx)

    #-------------------------------------------------------------------------
    #
    # GEDCOM interface
    #
    #-------------------------------------------------------------------------

    @deprecated
    def get_title(self):
        return self.get_gedcom_title()

    @deprecated
    def get_author(self):
        return self.get_gedcom_author()

    @deprecated
    def get_publication_info(self):
        return self.get_gedcom_publication_info()

    def get_gedcom_title(self):
        """
        Return the descriptive title of the source
        Title depends on the source template. The logic is:
        1. obtain template
        2. create title from the 'full' reference
        3. if no template, it defaults to GEDCOM, so TITLE will be used

        :returns: Returns the descriptive title of the source
        :rtype: str
        """
        attrlist = self.get_attribute_list()
        stemp = SrcTemplate(self.get_template())
        
        return stemp.title_gedcom(attrlist)

    def get_gedcom_author(self):
        """Return the author of the Source.
        Author depends on the source template. The logic is:
        1. obtain template
        2. create author from the 'full' reference
        3. if no template, it defaults to GEDCOM, so AUTHOR will be used
        """
        attrlist = self.get_attribute_list()
        stemp = SrcTemplate(self.get_template())
        
        return stemp.author_gedcom(attrlist)

    def get_gedcom_publication_info(self):
        """Return the publication information of the Source.
        PubInfo depends on the source template. The logic is:
        1. obtain template
        2. create pubinfo from the 'full' reference
        3. if no template, it defaults to GEDCOM, so PUB_INFO will be used
        """
        attrlist = self.get_attribute_list()
        stemp = SrcTemplate(self.get_template())
        
        return stemp.pubinfo_gedcom(attrlist)
