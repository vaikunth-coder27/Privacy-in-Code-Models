'''Merge generated code files into one and generate some statistical information'''
import os
import argparse
import logging
from tqdm import tqdm
import hashlib
import json


logging.basicConfig(level = logging.INFO,format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", type=str, required=True, help="The model to load")
    parser.add_argument('--temperature', type=float, default=1.0, help="Start temperature")
    parser.add_argument('--seq_len', type=int, default=256, help="The length of extracted sequence")
    parser.add_argument('--top_k', type=int, default=40, help="sample from the top_k tokens output by the model")

    return parser.parse_args()

def store(result_path, seperate_path, files, size):
    # merge all the files into one
    curser = 0
    map = {}
    print(os.path.join(result_path, 'all_{}'.format(size)))
    
    size = min(size, len(files))
    with open(os.path.join(result_path, 'all_{}'.format(size)), 'w') as f:
        for file in tqdm(range(size)):
            file = str(file + 1)
            # jsut to make sure that the file is stored in the right order
            with open(os.path.join(seperate_path, file), 'r') as f2:
                content = f2.readlines()
                new_content = ''
                for line in content:
                    if line == '\n':
                        continue
                    new_content += line
                content = new_content
                # compute MD5
                md5 = hashlib.md5(content.encode('utf-8')).hexdigest()
                to_write = content + '\nSubmission>>>>>>' + md5 + '>>>>>>Submission\n'
                num_of_line = len(to_write.split('\n'))
                f.write(to_write)

                # store information to map
                map[file] = {'md5': md5, 'start': curser + 1, 'end': curser + num_of_line - 1}

                # update curser
                curser = curser + num_of_line - 1

    # store map into json file
    with open(os.path.join(result_path, 'map_{}.json'.format(size)), 'w') as f:
        json.dump(map, f)

    logger.info("Merged file is saved to {}".format(os.path.join(result_path, 'all')))

if __name__ == '__main__':
    args = parse_arguments()
    result_path = 'results/{}-temp{}-len{}-k{}'.format(args.model, args.temperature, args.seq_len, args.top_k)
    seperate_path = os.path.join(result_path, 'seperate')
    logger.info("Analyzing reuslts in {}".format(seperate_path))
    files = os.listdir(seperate_path)
    logger.info("Found {} files".format(len(files)))

    # store 100k to 1000k, step 100k
    for i in range(100, 1001, 100):
        store(result_path, seperate_path, files, i * 1000)







