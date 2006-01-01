#
# Test check_id script
#

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Testing import ZopeTestCase
from Products.CMFPlone.tests import PloneTestCase


class TestExternalEditorEnabled(PloneTestCase.PloneTestCase):
    '''Tests the externalEditorEnabled script'''

    def afterSetUp(self):
        PloneTestCase.PloneTestCase.afterSetUp(self)
        self.folder.invokeFactory('Document','doc')
        self.doc = self.folder.doc
        self.folder.invokeFactory('Folder','folder2')
        self.folder = self.folder.folder2
        self.portal.acl_users._doAddUser('user1', 'secret', ['Member'], [])
        self.mtool = self.portal.portal_membership
        memb = self.mtool.getAuthenticatedMember()
        memb.manage_changeProperties(ext_editor=1)

        self.lockbody = ('<?xml version="1.0" encoding="utf-8"?>\n'
                '<d:lockinfo xmlns:d="DAV:">\n'
                '  <d:lockscope><d:exclusive/></d:lockscope>\n'
                '  <d:locktype><d:write/></d:locktype>\n'
                '  <d:depth>infinity</d:depth>\n'
                '  <d:owner>\n'
                '  <d:href>Zope External Editor</d:href>\n'
                '  </d:owner>\n'
                '</d:lockinfo>'
                )

    def testFailForAnonymous(self):
        self.failUnless(self.doc.externalEditorEnabled())
        self.logout()
        self.failIf(self.doc.externalEditorEnabled())

    def testFailOnDisabledMemberProperty(self):
        self.failUnless(self.doc.externalEditorEnabled())
        memb = self.mtool.getAuthenticatedMember()
        memb.manage_changeProperties(ext_editor=0)
        self.failIf(self.doc.externalEditorEnabled())

    def testFailOnUnSupportedObjects(self):
        # ATCT Folders are editable by default now
        self.failUnless(self.folder.externalEditorEnabled())
        # But if __dav_marshall__ is set to False then they aren't.
        self.folder.__dav_marshall__ = False
        self.failIf(self.folder.externalEditorEnabled())

    def testFailWithoutUseExtEditPermission(self):
        self.portal.manage_permission('Use external editor',
                                      ('Owner','Manager'), 0)
        self.login('user1')
        self.failIf(self.doc.externalEditorEnabled())

    def testFailWhenObjectIsLocked(self):
        # Should not show if someone already has a webdav lock on the object
        self.doc.REQUEST.set('BODY', self.lockbody)
        self.doc.LOCK(self.doc.REQUEST, self.doc.REQUEST.RESPONSE)
        self.failIf(self.doc.externalEditorEnabled())
        self.doc.wl_clearLocks()
        self.failUnless(self.doc.externalEditorEnabled())


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestExternalEditorEnabled))
    return suite

if __name__ == '__main__':
    framework()