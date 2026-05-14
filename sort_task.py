import sys
import os
import tempfile
import multiprocessing
import concurrent.futures
import heapq


def sort_numbers(filename: str, size: int):
    dir = tempfile.mkdtemp(dir=os.path.dirname(filename))
    
    parts: list = [] #for info
    start: int = 0
    
    while True:
        read_one = read_part(filename, start, 1)
        if not read_one:  # eof
            break
        
        parts.append((filename, start, size, dir))
        start += size
        
    cpu_count = multiprocessing.cpu_count()
    files = []
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=cpu_count) as executor:
        running_tasks = {} 

        for p in parts:
            future = executor.submit(sort_parts, p)
            running_tasks[future] = p # make dictionary
            
        for task in concurrent.futures.as_completed(running_tasks):
            file = task.result()
            files.append(file)
            
    output = os.path.join(
        os.path.dirname(filename),
        f"sorted_{os.path.basename(filename)}"
    )
    
    make_one_file(files, output)
    
    os.rmdir(dir) # remove unnecessary
    
    print(f"End of sort")
            
            
def sort_parts(args):
    filename, start, size, dir = args
    numbers = read_part(filename, start, size)
    numbers.sort()
    
    curr_file = tempfile.NamedTemporaryFile(delete=False, dir=dir, suffix='.txt')
    with open(curr_file.name, 'w') as f:
        for n in numbers:
            f.write(f"{n}\n") 
    
    return curr_file.name
    
    
def make_one_file(f_paths, output):
    open_files = []
    heap = []
    
    for i, f_path in enumerate(f_paths):
        f = open(f_path, 'r')
        open_files.append(f)
        line = f.readline()
        if line:
            num = int(line.strip())
            heapq.heappush(heap, (num, i))
        
    with open(output, 'w') as out_f:
        while heap:
            n, id = heapq.heappop(heap)
            out_f.write(f"{n}\n")
            
            line = open_files[id].readline()
            if line:
                next_num = int(line.strip())
                heapq.heappush(heap, (next_num, id))
                
    for f in open_files:
        f.close()
        
    for f_path in f_paths:
        os.unlink(f_path) 
            

def read_part(filename: str, start: int, size: int) -> list:
    lst: list = []
    with open(filename, 'r') as file:
        for _ in range(start):
            file.readline()
            
        for _ in range(size):   
            line = file.readline()
            if not line:
                break
            lst.append(int(line.strip()))
    return lst


def main():
    # на вход пожается название файла и количество чисел 
    name: str = sys.argv[1]
    size: int  = int(sys.argv[2])
    
    sort_numbers(name, size)


if __name__ == "__main__":
    main()
