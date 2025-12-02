import json
import os


def create_index_list(sliced_list):
    #creates indices tuples for slice of list
    index_tuples = []
    item_list = []
    start, end = 0, 0
    prev = sliced_list[0]
    for i in range(len(sliced_list)):
        if prev != sliced_list[i]:
            item_list.append(prev)
            end = i-1
            index_tuples.append((start, end))
            start = i
            prev = sliced_list[start]
    item_list.append(prev)
    index_tuples.append((end+1, len(sliced_list)-1))
    return index_tuples, item_list

def build_index_dict(sorted_list2d, output_dir):
    """
    Builds a dictionary where each unique element of a taxonomy level
    has a corresponding
    :param sorted_list2d:
    :param output_dir:
    :return:
    """
    taxonomy = ['genus','family','order','class','phylum','kingdom']
    index_dict = {}
                #{'taxonomy level' : [ [[start, end],...], ["name",...] ],...}

    for i in range(7, 1, -1):
        tax_name_list = [sorted_list2d[j][i] for j in range(len(sorted_list2d))]
        index_dict[taxonomy[i-2]] = create_index_list(tax_name_list)

    print("saving json of labels")
    with open(os.path.join(output_dir, 'tax_indices.json'), 'w') as f:
        json.dump(index_dict, f)

    return index_dict


#MOVE THIS TO SOME SORT OF INFERENCE FILE LATER
def sum_over_index_list(original_list, index_tuple_list):
    """
    Sums over a list of values using tuples of intervals to return
    a list of sums the size of the tuple list.
    This is used to sum the logits for a higher taxonomy level if species
    classification confidence is too low. When a confidence threshold is reached,
    the index of the largest element corresponds to the index of the name of
    the element in the taxonomy level where confidence was reached.
    :param original_list: a list of logits for every species
    :param index_tuple_list: a list of tuples [start, end] inclusive of each name
    where the difference is the number of species withing that taxonomy level name
    corresponds to the dict.keys() of the taxonomy level of interest
    :return:
    """
    sum_list = []
    for indices in index_tuple_list:
        sum_list.append(sum(original_list[indices[0]:indices[1]+1]))
    return sum_list