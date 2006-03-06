import string
from Products.CMFCore.utils import getToolByName

def two12_two13(portal):
    """2.1.2 -> 2.1.3
    """
    out = []

    # Put navtree properties in a sensible state
    normalizeNavtreeProperties(portal, out)
    
    return out

def normalizeNavtreeProperties(portal, out):
    """Remove unused navtree properties, add 'name' and 'root' properties. Set
    bottomLevel to 0 if it's 65535 (the old marker)
    """
    toRemove = ['skipIndex_html', 'showMyUserFolderOnly', 'showFolderishSiblingsOnly',
                'showFolderishChildrenOnly', 'showNonFolderishObject', 'showTopicResults',
                'rolesSeeContentView', 'rolesSeeUnpublishedContent', 'rolesSeeContentsView', 
                'batchSize', 'sortCriteria', 'croppingLength', 'forceParentsInBatch', 
                'rolesSeeHiddenContent', 'typesLinkToFolderContents']
    toAdd = {'name' : 'Navigation', 'root' : '/'}
    portal_properties = getToolByName(portal, 'portal_properties', None)
    if portal_properties is not None:
        navtree_properties = getattr(portal_properties, 'navtree_properties', None)
        if navtree_properties is not None:
            for property in toRemove:
                if navtree_properties.getProperty(property, None) is not None:
                    navtree_properties._delProperty(property)
            for property, value in toAdd.items():
                if navtree_properties.getProperty(property, None) is None:
                    navtree_properties._setProperty(property, value, 'string')
            bottomLevel = navtree_properties.getProperty('bottomLevel', None)
            if bottomLevel == 65535:
                navtree_properties.manage_changeProperties(bottomLevel = 0)