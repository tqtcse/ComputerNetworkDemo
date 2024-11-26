my_list = ["0", "0", "0"]

a = [1,2,4]

separator = ' '

my_list = ' '.join(my_list)




import os
pieceid = 'piece1'
current_work_dir = os.getcwd()
piecepath = '\\file2'
os.mkdir(current_work_dir + piecepath)

# piece_size = os.path.getsize(current_work_dir+piecepath)
# file = open(current_work_dir+piecepath, mode='r')
#
# data = file.read()
#
# print(data)
# print(piece_size)