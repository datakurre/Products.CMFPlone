#
# CatalogTool tests
#

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Testing import ZopeTestCase
from Products.PloneTestCase import PloneTestCase
PloneTestCase.setupPloneSite()

from Acquisition import aq_base
from Globals import REPLACEABLE
from DateTime import DateTime
from Products.CMFCore.permissions import AccessInactivePortalContent
import transaction

from Products.CMFPlone.CatalogTool import ExtensibleIndexableObjectWrapper
from Products.CMFPlone.CatalogTool import _eioRegistry

from Products.CMFPlone.CatalogTool import is_folderish
from Products.PloneTestCase import dummy

portal_name = PloneTestCase.portal_name
default_user  = PloneTestCase.default_user

user2  = 'u2'
group2 = 'g2'

base_content = ['Members', 'events', 'news', 'previous', default_user, 'doc']


class TestCatalogSetup(PloneTestCase.PloneTestCase):

    def afterSetUp(self):
        self.catalog = self.portal.portal_catalog

    def testSearchableTextIsZCTextIndex(self):
        # SearchableText index should be a ZCTextIndex
        itype = self.catalog.Indexes['SearchableText'].__class__.__name__
        self.assertEqual(itype, 'ZCTextIndex')

    def testDescriptionIsZCTextIndex(self):
        # Description index should be a ZCTextIndex
        itype = self.catalog.Indexes['Description'].__class__.__name__
        self.assertEqual(itype, 'ZCTextIndex')

    def testTitleIsZCTextIndex(self):
        # Title index should be a ZCTextIndex
        itype = self.catalog.Indexes['Title'].__class__.__name__
        self.assertEqual(itype, 'ZCTextIndex')

    def testPloneLexiconIsZCTextLexicon(self):
        # Lexicon should be a ZCTextIndex lexicon
        self.failUnless(hasattr(aq_base(self.catalog), 'plone_lexicon'))
        self.assertEqual(self.catalog.plone_lexicon.meta_type,\
                         'ZCTextIndex Lexicon')

    def testPathIsExtendedPathIndex(self):
        # path index should be an ExtendedPathIndex
        self.assertEqual(self.catalog.Indexes['path'].__class__.__name__,
                         'ExtendedPathIndex')

    def testGetObjPositionInParentIsFieldIndex(self):
        # getObjPositionInParent index should be a FieldIndex
        # also see TestCatalogOrdering below
        self.assertEqual(self.catalog.Indexes['getObjPositionInParent'].__class__.__name__,
                         'FieldIndex')

    def testGetObjSizeInSchema(self):
        # getObjSize column should be in catalog schema
        self.failUnless('getObjSize' in self.catalog.schema())

    def testExclude_from_navInSchema(self):
        # exclude_from_nav column should be in catalog schema
        self.failUnless('exclude_from_nav' in self.catalog.schema())

    def testIs_folderishInSchema(self):
        # is_folderish should be in catalog schema
        self.failUnless('is_folderish' in self.catalog.schema())

    def testIs_folderishIsFieldIndex(self):
        # is_folderish should be a FieldIndex
        self.failUnless(self.catalog.Indexes['is_folderish'].__class__.__name__,
                        'FieldIndex')

    def testDateIsDateIndex(self):
        # Date should be a DateIndex
        self.assertEqual(self.catalog.Indexes['Date'].__class__.__name__,
                         'DateIndex')

    def testCreatedIsDateIndex(self):
        # created should be a DateIndex
        self.assertEqual(self.catalog.Indexes['created'].__class__.__name__,
                         'DateIndex')

    def testEffectiveIsDateIndex(self):
        # effective should be a DateIndex
        self.assertEqual(self.catalog.Indexes['effective'].__class__.__name__,
                         'DateIndex')

    def testEndIsDateIndex(self):
        # end should be a DateIndex
        self.assertEqual(self.catalog.Indexes['end'].__class__.__name__,
                         'DateIndex')

    def testExpiresIsDateIndex(self):
        # expires should be a DateIndex
        self.assertEqual(self.catalog.Indexes['expires'].__class__.__name__,
                         'DateIndex')

    def testModifiedIsDateIndex(self):
        # modified should be a DateIndex
        self.assertEqual(self.catalog.Indexes['modified'].__class__.__name__,
                         'DateIndex')

    def testStartIsDateIndex(self):
        # start should be a DateIndex
        self.assertEqual(self.catalog.Indexes['start'].__class__.__name__,
                         'DateIndex')

    def testEffectiveRangeIsDateRangeIndex(self):
        # effectiveRange should be a DateRangeIndex
        self.assertEqual(self.catalog.Indexes['effectiveRange'].__class__.__name__,
                         'DateRangeIndex')

    def testSortable_TitleIsFieldIndex(self):
        # sortable_title should be a FieldIndex
        self.assertEqual(self.catalog.Indexes['sortable_title'].__class__.__name__,
                         'FieldIndex')

    def testExpirationDateInSchema(self):
        # ExpirationDate column should be in catalog schema
        self.failUnless('ExpirationDate' in self.catalog.schema())

    def testExpiresDateNotInSchema(self):
        # ExpirationDate column should be in catalog schema
        self.failIf('ExpiresDate' in self.catalog.schema())

    def testIs_Default_PageIsFieldIndex(self):
        # sortable_title should be a FieldIndex
        self.assertEqual(self.catalog.Indexes['is_default_page'].__class__.__name__,
                         'FieldIndex')


class TestCatalogIndexing(PloneTestCase.PloneTestCase):

    def afterSetUp(self):
        self.catalog = self.portal.portal_catalog
        self.folder.invokeFactory('Document', id='doc', title='Foo', description='Bar')
        self.catalog.unindexObject(self.folder.doc)

    def testFixture(self):
        self.assertEqual(self.folder.doc.getId(), 'doc')
        self.assertEqual(self.folder.doc.Title(), 'Foo')
        self.assertEqual(self.folder.doc.Description(), 'Bar')
        self.assertEqual(len(self.catalog(id='doc')), 0)
        self.assertEqual(len(self.catalog(Title='Foo')), 0)
        self.assertEqual(len(self.catalog(Description='Bar')), 0)

    def testIndexObject(self):
        # Object should be indexed
        self.catalog.indexObject(self.folder.doc)
        self.assertEqual(len(self.catalog(id='doc')), 1)
        self.assertEqual(len(self.catalog(Title='Foo')), 1)
        self.assertEqual(len(self.catalog(Description='Bar')), 1)

    def testReindexObject(self):
        # Object should be indexed
        self.catalog.reindexObject(self.folder.doc)
        self.assertEqual(len(self.catalog(id='doc')), 1)
        self.assertEqual(len(self.catalog(Title='Foo')), 1)
        self.assertEqual(len(self.catalog(Description='Bar')), 1)

    def testUnindexObject(self):
        # Object should be unindexed
        self.catalog.indexObject(self.folder.doc)
        self.assertEqual(len(self.catalog(id='doc')), 1)
        self.catalog.unindexObject(self.folder.doc)
        self.assertEqual(len(self.catalog(id='doc')), 0)

    def testIndexObjectUpdatesMetadata(self):
        # Indexing should update metadata
        self.catalog.indexObject(self.folder.doc)
        brain = self.catalog(id='doc')[0]
        self.assertEqual(brain.id, 'doc')
        self.assertEqual(brain.Title, 'Foo')
        self.assertEqual(brain.Description, 'Bar')

    def testReindexObjectUpdatesMetadata(self):
        # Reindexing should update metadata
        self.catalog.indexObject(self.folder.doc)
        self.folder.doc.setTitle('Fred')
        self.folder.doc.setDescription('BamBam')
        self.catalog.reindexObject(self.folder.doc)
        brain = self.catalog(id='doc')[0]
        self.assertEqual(brain.id, 'doc')
        self.assertEqual(brain.Title, 'Fred')
        self.assertEqual(brain.Description, 'BamBam')

    def testReindexObjectSkipsMetadata(self):
        # Reindexing should not update metadata when update_metadata=0
        self.catalog.indexObject(self.folder.doc)
        self.folder.doc.setTitle('Fred')
        self.folder.doc.setDescription('BamBam')
        self.catalog.reindexObject(self.folder.doc, update_metadata=0)
        brain = self.catalog(id='doc')[0]
        # Metadata did not change
        self.assertEqual(brain.id, 'doc')
        self.assertEqual(brain.Title, 'Foo')
        self.assertEqual(brain.Description, 'Bar')

    def testReindexTitleOnly(self):
        # Reindexing should only index the Title
        self.catalog.indexObject(self.folder.doc)
        self.folder.doc.setTitle('Fred')
        self.folder.doc.setDescription('BamBam')
        self.catalog.reindexObject(self.folder.doc, idxs=['Title'])
        self.assertEqual(len(self.catalog(id='doc')), 1)
        self.assertEqual(len(self.catalog(Title='Fred')), 1)
        # Description index did not change
        self.assertEqual(len(self.catalog(Description='Bar')), 1)
        self.assertEqual(len(self.catalog(Description='BamBam')), 0)

    def testReindexTitleOnlyUpdatesMetadata(self):
        # Reindexing Title should update metadata
        self.catalog.indexObject(self.folder.doc)
        self.folder.doc.setTitle('Fred')
        self.folder.doc.setDescription('BamBam')
        self.catalog.reindexObject(self.folder.doc, idxs=['Title'])
        brain = self.catalog(id='doc')[0]
        self.assertEqual(brain.id, 'doc')
        self.assertEqual(brain.Title, 'Fred')
        self.assertEqual(brain.Description, 'BamBam')

    def testReindexTitleOnlySkipsMetadata(self):
        # Reindexing Title should not update metadata when update_metadata=0
        self.catalog.indexObject(self.folder.doc)
        self.folder.doc.setTitle('Fred')
        self.folder.doc.setDescription('BamBam')
        self.catalog.reindexObject(self.folder.doc, idxs=['Title'], update_metadata=0)
        brain = self.catalog(id='doc')[0]
        # Metadata did not change
        self.assertEqual(brain.id, 'doc')
        self.assertEqual(brain.Title, 'Foo')
        self.assertEqual(brain.Description, 'Bar')

    def testIndexTitleOnly(self):
        # Indexing should only index the Title
        #
        # TODO: This does not work as expected. The object
        # appears to be in the catalog but is not returned
        # by searchResults()!?
        #
        self.catalog.indexObject(self.folder.doc, idxs=['Title'])
        # The document is cataloged
        path = self.catalog._CatalogTool__url(self.folder.doc)
        self.failUnless(path in self.catalog._catalog.paths.values())
        # But it is not returned when searching...
        self.assertEqual(len(self.catalog(id='doc')), 0)
        self.assertEqual(len(self.catalog(Title='Foo')), 0) # <-- Should be 1
        self.assertEqual(len(self.catalog(Description='Bar')), 0)

    def testIndexIdOnly(self):
        # Indexing should only index the id
        #
        # TODO: Demonstrate that the behavior is independent
        # of index type.
        #
        self.catalog.indexObject(self.folder.doc, idxs=['id'])
        # The document is cataloged
        path = self.catalog._CatalogTool__url(self.folder.doc)
        self.failUnless(path in self.catalog._catalog.paths.values())
        # But it is not returned when searching...
        self.assertEqual(len(self.catalog(id='doc')), 0) # <-- Should be 1
        self.assertEqual(len(self.catalog(Title='Foo')), 0)
        self.assertEqual(len(self.catalog(Description='Bar')), 0)


class TestCatalogSearching(PloneTestCase.PloneTestCase):

    def afterSetUp(self):
        self.catalog = self.portal.portal_catalog
        self.workflow = self.portal.portal_workflow
        self.groups = self.portal.portal_groups

        self.portal.acl_users._doAddUser(user2, 'secret', [], [])

        self.folder.invokeFactory('Document', id='doc', text='foo')
        self.folder.invokeFactory('Folder', id='folder2')
        self.folder.folder2.invokeFactory('Document', id='doc2', text='bar')
        self.workflow.doActionFor(self.folder.doc, 'hide', comment='')
        self.workflow.doActionFor(self.folder.folder2, 'hide', comment='')
        self.workflow.doActionFor(self.folder.folder2.doc2, 'hide', comment='')

        # Used for testing AND/OR search functionality below
        self.folder.invokeFactory('Document', id='aaa', text='aaa', title='ccc')
        self.folder.invokeFactory('Document', id='bbb', text='bbb')

    def addUser2ToGroup(self):
        self.groups.groupWorkspacesCreationFlag = 0
        self.groups.addGroup(group2, None, [], [])
        group = self.groups.getGroupById(group2)
        group.addMember(user2)
        prefix = self.portal.acl_users.getGroupPrefix()
        return '%s%s' % (prefix, group2)

    def testListAllowedRolesAndUsers(self):
        # Should include the group in list of allowed users
        groupname = self.addUser2ToGroup()
        uf = self.portal.acl_users
        self.failUnless(('user:%s' % groupname) in
                self.catalog._listAllowedRolesAndUsers(uf.getUser(user2)))

    def testSearchReturnsDocument(self):
        # Document should be found when owner does a search
        self.assertEqual(self.catalog(SearchableText='foo')[0].id, 'doc')

    def testSearchDoesNotReturnDocument(self):
        # Document should not be found when user2 does a search
        self.login(user2)
        self.assertEqual(len(self.catalog(SearchableText='foo')), 0)

    def testSearchReturnsDocumentUsing_DefaultAND(self):
        # Documents should not be found when searching 'aaa bbb' (which should default to AND)
        self.assertEqual(len(self.catalog(SearchableText='aaa bbb')), 0)
        self.assertEqual(len(self.catalog(SearchableText='aaa ccc')), 1)

    def testSearchReturnsDocumentUsing_AND(self):
        # Documents should not be found when owner does a search using AND
        self.assertEqual(len(self.catalog(SearchableText='aaa AND bbb')), 0)
        self.assertEqual(len(self.catalog(SearchableText='aaa AND ccc')), 1)

    def testSearchReturnsDocumentUsing_OR(self):
        # Two documents (aaa, bbb)  should be found when owner does a search using OR 
        results = self.catalog(SearchableText='aaa OR bbb')
        self.assertEqual(len(results), 2)

    def testSearchReturnsDocumentWhenPermissionIsTroughLocalRole(self):
        # After adding a group with access rights and containing user2,
        # a search must find the document.
        groupname = self.addUser2ToGroup()
        self.folder.folder_localrole_edit('add', [groupname], 'Owner')
        self.login(user2)
        self.assertEqual(self.catalog(SearchableText='foo')[0].id, 'doc')

    def testSearchRespectsLocalRoleAcquisition(self):
        # After adding a group with access rights and containing user2,
        # a search must find the document in subfolders.
        groupname = self.addUser2ToGroup()
        self.folder.folder_localrole_edit('add', [groupname], 'Owner')
        self.login(user2)
        # Local Role works in subfolder
        self.assertEqual(self.catalog(SearchableText='bar')[0].id, 'doc2')

    def testSearchRespectsLocalRoleAcquisitionDisabled(self):
        # After adding a group with access rights and containing user2,
        # a search should not find documents in subfolders which have
        # disabled local role acquisition.
        groupname = self.addUser2ToGroup()
        self.folder.folder_localrole_edit('add', [groupname], 'Owner')
        # Acquisition off for folder2
        self.login(default_user)
        self.folder.folder2.folder_localrole_set(use_acquisition=0)
        #Everything in subfolder should be invisible
        self.login(user2)
        self.failIf(self.catalog(SearchableText='bar'))


class TestCatalogSorting(PloneTestCase.PloneTestCase):

    def afterSetUp(self):
        self.catalog = self.portal.portal_catalog

        self.folder.invokeFactory('Document', id='doc', text='foo')
        self.folder.doc.setTitle('12 Document 25')
        self.folder.invokeFactory('Document', id='doc2', text='foo')
        self.folder.doc2.setTitle('3 Document 4')
        self.folder.invokeFactory('Document', id='doc3', text='foo')
        self.folder.doc3.setTitle('12 Document 4')

        self.folder.invokeFactory('Document', id='doc4', text='bar')
        self.folder.doc4.setTitle('document 12')
        self.folder.invokeFactory('Document', id='doc5', text='bar')
        self.folder.doc5.setTitle('Document 2')
        self.folder.invokeFactory('Document', id='doc6', text='bar')
        self.folder.doc6.setTitle('DOCUMENT 4')
        self.folder.doc.reindexObject()
        self.folder.doc2.reindexObject()
        self.folder.doc3.reindexObject()
        self.folder.doc4.reindexObject()
        self.folder.doc5.reindexObject()
        self.folder.doc6.reindexObject()

    def testSortTitleReturnsProperOrderForNumbers(self):
        # Documents should be returned in proper numeric order
        results = self.catalog(SearchableText='foo', sort_on='sortable_title')
        self.assertEqual(results[0].getId, 'doc2')
        self.assertEqual(results[1].getId, 'doc3')
        self.assertEqual(results[2].getId, 'doc')

    def testSortTitleIgnoresCase(self):
        # Documents should be returned in case insensitive order
        results = self.catalog(SearchableText='bar', sort_on='sortable_title')
        self.assertEqual(results[0].getId, 'doc5')
        self.assertEqual(results[1].getId, 'doc6')
        self.assertEqual(results[2].getId, 'doc4')

    def testSortableTitleOutput(self):
        doc = self.folder.doc
        wrapped = ExtensibleIndexableObjectWrapper(vars, doc, self.portal)
        
        self.assertEqual(wrapped.sortable_title, u'00000012 document 00000025')

    def testSortableNonASCIITitles(self):
        #test a utf-8 encoded string gets properly unicode converted
        title = 'La Pe\xc3\xb1a'
        doc = self.folder.doc
        doc.setTitle(title)
        wrapped = ExtensibleIndexableObjectWrapper(vars, doc, self.portal)
        self.assertEqual(wrapped.sortable_title, u'la pe\xf1a'.encode('utf-8'))


class TestFolderCataloging(PloneTestCase.PloneTestCase):
    # Tests for http://plone.org/collector/2876
    # folder_edit must recatalog. folder_rename must recatalog.

    def afterSetUp(self):
        self.catalog = self.portal.portal_catalog
        self.folder.invokeFactory('Folder', id='foo')

    def testFolderTitleIsUpdatedOnEdit(self):
        # Test for catalog that searches to ensure folder titles are 
        # updated in the catalog. 
        title = 'Test Folder - Snooze!'
        self.folder.foo.folder_edit(title, '')
        results = self.catalog(Title='Snooze')
        self.failUnless(results)
        for result in results:
            self.assertEqual(result.Title, title)
            self.assertEqual(result.id, 'foo')

    def testFolderTitleIsUpdatedOnRename(self):
        # Test for catalog that searches to ensure folder titles are 
        # updated in the catalog. 
        title = 'Test Folder - Snooze!'
        transaction.savepoint(optimistic=True) # make rename work
        self.folder.foo.folder_edit(title, '', id='bar')
        results = self.catalog(Title='Snooze')
        self.failUnless(results)
        for result in results:
            self.assertEqual(result.Title, title)
            self.assertEqual(result.id, 'bar')

    def testFolderTitleIsUpdatedOnFolderTitleChange(self):
        # The bug in fact talks about folder_rename
        title = 'Test Folder - Snooze!'
        foo_path = '/'.join(self.folder.foo.getPhysicalPath())
        self.folder.folder_rename(paths=[foo_path], new_ids=['foo'], new_titles=[title])
        results = self.catalog(Title='Snooze')
        self.failUnless(results)
        for result in results:
            self.assertEqual(result.Title, title)
            self.assertEqual(result.id, 'foo')

    def testFolderTitleIsUpdatedOnFolderRename(self):
        # The bug in fact talks about folder_rename
        title = 'Test Folder - Snooze!'
        transaction.savepoint(optimistic=True) # make rename work
        foo_path = '/'.join(self.folder.foo.getPhysicalPath())
        self.folder.folder_rename(paths=[foo_path], new_ids=['bar'], new_titles=[title])
        results = self.catalog(Title='Snooze')
        self.failUnless(results)
        for result in results:
            self.assertEqual(result.Title, title)
            self.assertEqual(result.id, 'bar')

    def testSetTitleDoesNotUpdateCatalog(self):
        # setTitle() should not update the catalog
        title = 'Test Folder - Snooze!'
        self.failUnless(self.catalog(id='foo'))
        self.folder.foo.setTitle(title)
        #Title is a TextIndex
        self.failIf(self.catalog(Title='Snooze'))


class TestCatalogOrdering(PloneTestCase.PloneTestCase):

    def afterSetUp(self):
        self.catalog = self.portal.portal_catalog
        self.folder.invokeFactory('Document', id='doc1', text='foo')
        self.folder.invokeFactory('Document', id='doc2', text='bar')
        self.folder.invokeFactory('Document', id='doc3', text='bloo')
        self.folder.invokeFactory('Document', id='doc4', text='blee')

    def testInitialOrder(self):
        self.failUnlessEqual(self.folder.getObjectPosition('doc1'), 0)
        self.failUnlessEqual(self.folder.getObjectPosition('doc2'), 1)
        self.failUnlessEqual(self.folder.getObjectPosition('doc3'), 2)
        self.failUnlessEqual(self.folder.getObjectPosition('doc4'), 3)

    def testOrderIsUpdatedOnMoveDown(self):
        self.folder.folder_position('down','doc1')
        folder_docs = self.catalog(portal_type = 'Document',
                                   path = self.folder.getPhysicalPath(),
                                   sort_on = 'getObjPositionInParent')
        expected = ['doc2','doc1','doc3','doc4']
        self.failUnlessEqual([b.getId for b in folder_docs], expected)

    def testOrderIsUpdatedOnMoveUp(self):
        self.folder.folder_position('up','doc3')
        folder_docs = self.catalog(portal_type = 'Document',
                                   path = self.folder.getPhysicalPath(),
                                   sort_on = 'getObjPositionInParent')
        expected = ['doc1','doc3','doc2','doc4']
        self.failUnlessEqual([b.getId for b in folder_docs], expected)

    def testOrderIsUpdatedOnMoveTop(self):
        self.folder.folder_position('top','doc3')
        folder_docs = self.catalog(portal_type = 'Document',
                                   path = self.folder.getPhysicalPath(),
                                   sort_on = 'getObjPositionInParent')
        expected = ['doc3','doc1','doc2','doc4']
        self.failUnlessEqual([b.getId for b in folder_docs], expected)

    def testOrderIsUpdatedOnMoveBottom(self):
        self.folder.folder_position('bottom','doc3')
        folder_docs = self.catalog(portal_type = 'Document',
                                   path = self.folder.getPhysicalPath(),
                                   sort_on = 'getObjPositionInParent')
        expected = ['doc1','doc2','doc4','doc3']
        self.failUnlessEqual([b.getId for b in folder_docs], expected)

    def testOrderIsFineWithObjectCreation(self):
        self.folder.invokeFactory('Document', id='doc5', text='blam')
        folder_docs = self.catalog(portal_type = 'Document',
                                   path = self.folder.getPhysicalPath(),
                                   sort_on = 'getObjPositionInParent')
        expected = ['doc1','doc2','doc3','doc4','doc5']
        self.failUnlessEqual([b.getId for b in folder_docs], expected)

    def testOrderIsFineWithObjectDeletion(self):
        self.folder.manage_delObjects(['doc3',])
        folder_docs = self.catalog(portal_type = 'Document',
                                   path = self.folder.getPhysicalPath(),
                                   sort_on = 'getObjPositionInParent')
        expected = ['doc1','doc2','doc4']
        self.failUnlessEqual([b.getId for b in folder_docs], expected)

    def testOrderIsFineWithObjectRenaming(self):

        # I don't know why this is failing. manage_renameObjects throws an error
        # that blames permissions or lack of support by the obj. The obj is a
        # Plone Document, and the owner of doc2 is portal_owner. Harumph.

        transaction.savepoint(optimistic=True)

        self.folder.manage_renameObjects(['doc2'], ['buzz'])
        folder_docs = self.catalog(portal_type = 'Document',
                                   path = self.folder.getPhysicalPath(),
                                   sort_on = 'getObjPositionInParent')
        expected = ['doc1','buzz','doc3','doc4']
        self.failUnlessEqual([b.getId for b in folder_docs], expected)

    def testOrderAfterALotOfChanges(self):
        # ['doc1','doc2','doc3','doc4']

        self.folder.folder_position('down','doc1')
        self.folder.folder_position('down','doc1')
        # ['doc2','doc3','doc1','doc4']

        self.folder.folder_position('top','doc3')
        # ['doc3','doc2','doc1','doc4']

        self.folder.invokeFactory('Document', id='doc5', text='blam')
        self.folder.invokeFactory('Document', id='doc6', text='blam')
        self.folder.invokeFactory('Document', id='doc7', text='blam')
        self.folder.invokeFactory('Document', id='doc8', text='blam')
        # ['doc3','doc2','doc1','doc4','doc5','doc6','doc7','doc8',]

        #self.folder.manage_renameObjects('Document', id='doc5', text='blam')

        self.folder.manage_delObjects(['doc3','doc4','doc5','doc7'])
        expected = ['doc2','doc1','doc6','doc8']

        folder_docs = self.catalog(portal_type = 'Document',
                                   path = self.folder.getPhysicalPath(),
                                   sort_on = 'getObjPositionInParent')
        self.failUnlessEqual([b.getId for b in folder_docs], expected)

    def testAllObjectsHaveOrder(self):
        #Make sure that a query with sort_on='getObjPositionInParent'
        #returns the same number of results as one without, make sure
        #the Members folder is in the catalog and has getObjPositionInParent
        all_objs = self.catalog()
        sorted_objs = self.catalog(sort_on='getObjPositionInParent')
        self.failUnlessEqual(len(all_objs), len(sorted_objs))
        
        members = self.portal.Members
        members_path = '/'.join(members.getPhysicalPath())
        members_query = self.catalog(path=members_path)
        members_sorted = self.catalog(path=members_path, sort_on = 'getObjPositionInParent')
        self.failUnless(len(members_query))
        self.failUnlessEqual(len(members_query),len(members_sorted))


class TestCatalogBugs(PloneTestCase.PloneTestCase):

    def afterSetUp(self):
        self.catalog = self.portal.portal_catalog

    def testCanPastePortalIfLexiconExists(self):
        # Should be able to copy/paste a portal containing
        # a catalog tool. Triggers manage_afterAdd of portal_catalog
        # thereby exposing a bug which is now going to be fixed.
        self.loginPortalOwner()
        cb = self.app.manage_copyObjects([portal_name])
        self.app.manage_pasteObjects(cb)
        self.failUnless(hasattr(self.app, 'copy_of_'+portal_name))

    def testCanPasteCatalog(self):
        # Should be able to copy/paste a portal_catalog. Triggers
        # manage_afterAdd of portal_catalog thereby exposing another bug :-/
        self.setRoles(['Manager'])
        self.catalog.__replaceable__ = REPLACEABLE
        cb = self.portal.manage_copyObjects(['portal_catalog'])
        self.folder.manage_pasteObjects(cb)
        self.failUnless(hasattr(aq_base(self.folder), 'portal_catalog'))

    def testPastingCatalogPreservesTextIndexes(self):
        # Pasting the catalog should not cause indexes to be removed.
        self.setRoles(['Manager'])
        self.catalog.__replaceable__ = REPLACEABLE
        cb = self.portal.manage_copyObjects(['portal_catalog'])
        self.folder.manage_pasteObjects(cb)
        self.failUnless(hasattr(aq_base(self.folder), 'portal_catalog'))
        cat = self.folder.portal_catalog
        self.failUnless('SearchableText' in cat.indexes())
        # CMF added lexicons should stick around too
        self.failUnless(hasattr(aq_base(cat), 'plaintext_lexicon'))

    def testCanRenamePortalIfLexiconExists(self):
        # Should be able to rename a Plone portal
        # This test is to demonstrate that http://plone.org/collector/1745
        # is fixed and can be closed.
        self.loginPortalOwner()
        self.app.manage_renameObjects([portal_name], ['foo'])
        self.failUnless(hasattr(self.app, 'foo'))


class TestCatalogUnindexing(PloneTestCase.PloneTestCase):
    # Tests for http://plone.org/collector/3547
    # Published objects are not unindexed on delete?

    def afterSetUp(self):
        self.catalog = self.portal.portal_catalog
        self.workflow = self.portal.portal_workflow
        self.folder.invokeFactory('Document', id='doc')

    def testVisibleIsDefault(self):
        state = self.workflow.getInfoFor(self.folder.doc, 'review_state')
        self.assertEqual(state, 'visible')

    def testVisibleCanBeFound(self):
        self.failUnless(self.catalog(id='doc'))

    def testVisibleIsUnindexed(self):
        self.folder._delObject('doc')
        self.failIf(self.catalog(id='doc'))

    def testPrivateCanBeFound(self):
        self.workflow.doActionFor(self.folder.doc, 'hide')
        self.failUnless(self.catalog(id='doc'))

    def testPrivateIsUnindexed(self):
        self.workflow.doActionFor(self.folder.doc, 'hide')
        self.folder._delObject('doc')
        self.failIf(self.catalog(id='doc'))

    def testPendingCanBeFound(self):
        self.workflow.doActionFor(self.folder.doc, 'submit')
        self.failUnless(self.catalog(id='doc'))

    def testPendingIsUnindexed(self):
        self.workflow.doActionFor(self.folder.doc, 'submit')
        self.folder._delObject('doc')
        self.failIf(self.catalog(id='doc'))

    def testPublishedCanBeFound(self):
        self.setRoles(['Manager'])
        self.workflow.doActionFor(self.folder.doc, 'publish')
        self.failUnless(self.catalog(id='doc'))

    def testPublishedIsUnindexed(self):
        # Works here!
        self.setRoles(['Manager'])
        self.workflow.doActionFor(self.folder.doc, 'publish')
        self.folder._delObject('doc')
        self.failIf(self.catalog(id='doc'))

    def testPublishedIsUnindexedIfOwnerDeletes(self):
        # Works here!
        self.setRoles(['Manager'])
        self.workflow.doActionFor(self.folder.doc, 'publish')
        self.setRoles(['Member'])
        self.folder._delObject('doc')
        self.failIf(self.catalog(id='doc'))

    def testPublishedIsUnindexedByFolderDeleteScript(self):
        # Works here too!
        self.setRoles(['Manager'])
        self.workflow.doActionFor(self.folder.doc, 'publish')
        self.setRoles(['Member'])
        doc_path = '/'.join(self.folder.doc.getPhysicalPath())
        self.app.REQUEST.set('paths', [doc_path])
        self.folder.folder_delete()
        self.failIf(self.catalog(id='doc'))

    def testPublishedIsUnindexedWhenDeletingParentFolder(self):
        # Works here too!
        self.setRoles(['Manager'])
        self.workflow.doActionFor(self.folder.doc, 'publish')
        self.setRoles(['Member'])
        self.folder.aq_parent._delObject(self.folder.getId())
        self.failIf(self.catalog(id='doc'))


class TestCatalogExpirationFiltering(PloneTestCase.PloneTestCase):

    def afterSetUp(self):
        self.catalog = self.portal.portal_catalog
        self.folder.invokeFactory('Document', id='doc')

    def nofx(self):
        # Removes effective and expires to make sure we only test
        # the DateRangeIndex.
        self.catalog.delIndex('effective')
        self.catalog.delIndex('expires')

    def assertResults(self, result, expect):
        # Verifies ids of catalog results against expected ids
        lhs = [r.getId for r in result]
        lhs.sort()
        rhs = list(expect)
        rhs.sort()
        self.assertEqual(lhs, rhs)

    def testCeilingPatch(self):
        self.assertEqual(self.folder.doc.expires(), DateTime(2500, 0))

    def testSearchResults(self):
        res = self.catalog.searchResults()
        self.assertResults(res, base_content)

    def testCall(self):
        res = self.catalog()
        self.assertResults(res, base_content)

    def testSearchResultsExpired(self):
        self.folder.doc.setExpirationDate(DateTime(2000, 12, 31))
        self.folder.doc.reindexObject()
        self.nofx()
        res = self.catalog.searchResults()
        self.assertResults(res, base_content[:-1])

    def testCallExpired(self):
        self.folder.doc.setExpirationDate(DateTime(2000, 12, 31))
        self.folder.doc.reindexObject()
        self.nofx()
        res = self.catalog()
        self.assertResults(res, base_content[:-1])

    def testSearchResultsExpiredWithExpiredDisabled(self):
        self.folder.doc.setExpirationDate(DateTime(2000, 12, 31))
        self.folder.doc.reindexObject()
        self.nofx()
        res = self.catalog.searchResults(show_inactive=True)
        self.assertResults(res, base_content)

    def testCallExpiredWithExpiredDisabled(self):
        self.folder.doc.setExpirationDate(DateTime(2000, 12, 31))
        self.folder.doc.reindexObject()
        self.nofx()
        res = self.catalog(show_inactive=True)
        self.assertResults(res, base_content)

    def testSearchResultsExpiredWithPermission(self):
        self.folder.doc.setExpirationDate(DateTime(2000, 12, 31))
        self.folder.doc.reindexObject()
        self.nofx()
        self.setPermissions([AccessInactivePortalContent])
        res = self.catalog.searchResults()
        self.assertResults(res, base_content)

    def testCallExpiredWithPermission(self):
        self.folder.doc.setExpirationDate(DateTime(2000, 12, 31))
        self.folder.doc.reindexObject()
        self.nofx()
        self.setPermissions([AccessInactivePortalContent])
        res = self.catalog()
        self.assertResults(res, base_content)


def dummyMethod(obj, **kwargs):
    return 'a dummy'

class TestExtensibleIndexableObjectWrapper(PloneTestCase.PloneTestCase):
    """Tests for the wrapper
    """
    
    def afterSetUp(self):
        self.folder.invokeFactory('Document', 'doc', title='document')
        self.doc = self.folder.doc
        _eioRegistry.register('dummy', dummyMethod)
        
    def testSetup(self):
        doc = self.doc
        self.failUnlessEqual(doc.getId(), 'doc')
        self.failUnlessEqual(doc.Title(), 'document')
        
    def testWrapper(self):
        doc = self.doc
        vars = {'var' : 'a var'}
        wrapped = ExtensibleIndexableObjectWrapper(vars, doc, self.portal)
        self.failUnlessEqual(wrapped.var, 'a var')
        self.failUnlessEqual(wrapped.getId(), 'doc')
        self.failUnlessEqual(wrapped.Title(), 'document')
        self.failUnlessEqual(wrapped.dummy, 'a dummy')
        
    def beforeTearDown(self):
        _eioRegistry.unregister('dummy')

    def test_is_folderishWithNonFolder(self):
        i = dummy.Item()
        self.failIf(is_folderish(i))

    def test_is_folderishWithFolder(self):
        f = dummy.Folder('struct_folder')
        self.failUnless(is_folderish(f))

    def test_is_folderishWithNonStructuralFolder(self):
        f = dummy.NonStructuralFolder('ns_folder')
        self.failIf(is_folderish(f))


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestCatalogSetup))
    suite.addTest(makeSuite(TestCatalogIndexing))
    suite.addTest(makeSuite(TestCatalogSearching))
    suite.addTest(makeSuite(TestFolderCataloging))
    suite.addTest(makeSuite(TestCatalogOrdering))
    suite.addTest(makeSuite(TestCatalogBugs))
    suite.addTest(makeSuite(TestCatalogUnindexing))
    suite.addTest(makeSuite(TestCatalogExpirationFiltering))
    suite.addTest(makeSuite(TestExtensibleIndexableObjectWrapper))
    suite.addTest(makeSuite(TestCatalogSorting))
    return suite

if __name__ == '__main__':
    framework()
