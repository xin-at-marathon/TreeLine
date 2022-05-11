def format_output_ext(node, plainText=False, keepBlanks=False, spotRef=None):
    """Return a list of formatted text output lines with DSO extention.

    Arguments:
        node -- the node used to get data for fields
        plainText -- if True, remove HTML markup from fields and formats
        keepBlanks -- if True, keep lines with empty fields
        spotRef -- optional, used for ancestor field refs
    """

    if node.formatRef.name == 'INCLUDE':
        return __format_output_included_node(node, plainText, keepBlanks, spotRef)
    else:
        return __format_output_descendant(node, plainText, keepBlanks, spotRef)


def __format_output_included_node(include_node, plainText=False, keepBlanks=False, spotRef=None):
    included_node_uid = __get_included_node_uid(include_node)
    included_node = __find_node_by_uid(include_node, included_node_uid)
    if included_node == None:
        raise Exception(f'the included node with uid {included_node_uid} does not exist')

    alltext=[]
    for child in included_node.childList:
        alltext.extend(format_output_ext(child, plainText, keepBlanks, spotRef))
        if child.formatRef.spaceBetween:
            alltext.append('')

    return alltext

def __format_output_descendant(node, plainText=False, keepBlanks=False, spotRef=None):
        result = node.formatRef.formatOutput(node, plainText, keepBlanks, spotRef)

        mark = "{*@DescendantOutput*}"

        mark_str_index = -1
        mark_line = ''
        mark_line_index = -1

        for line in result:
            mark_line_index = result.index(line)

            mark_str_index = line.find(mark)
            if mark_str_index >= 0:
                mark_line=line
                break

        if mark_str_index >= 0:
            alltext=[]
            alltext.extend(result[:mark_line_index])
            
            if mark_line[:mark_str_index]:
                alltext.append(mark_line[:mark_str_index])

            for child in node.childList:
                alltext.extend(format_output_ext(child, plainText, keepBlanks, spotRef))
                if child.formatRef.spaceBetween:
                    alltext.append('')

            if mark_line[mark_str_index+len(mark):]:
                alltext.append(mark_line[mark_str_index+len(mark):])
                
            alltext.extend(result[mark_line_index+1:])
            return alltext

        else:
            for child in node.childList:
                result.extend(format_output_ext(child, plainText, keepBlanks, spotRef))
                if child.formatRef.spaceBetween:
                    result.append('')

            return result

def __get_included_node_uid(node):
    tag = node.data['Name']
    if not tag.startswith('<a href="#'):
        raise Exception('not a include node')
    return tag[10:].split('"')[0]
        
def __find_node_by_uid(node, uid):
    for node in node.treeStructureRef().descendantGen():
        if node.uId == uid:
            return node
    return None
