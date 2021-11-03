import pickle

# 列表
# 存储
# list1 = [123, 'xiaopingguo', 54, [90, 78]]
# list_file =

# a=pickle.load(open('/home/fandong/Code/object_detection_evaluation/src/database/yolov3-v410&EVT2', 'rb'))
# print(a)
# print(a)
# print(a)
# print(a)
# print(a)
# print(a)
# print(a)
with open('/home/fandong/Code/object_detection_evaluation/src/database/yolov3-v410&EVT2', 'rb') as f:
    while True:
        try:
            aa = pickle.load(f)
            print(aa)
        except EOFError:
            break
# list_file.close()
#
# with open('test','ab') as f:
#     pickle.dump('123',f)
#     pickle.dump('456',f)
#     f.close()
# with open('test','ab') as f:
#     pickle.dump('789',f)
#     f.close()
# with open('test','rb') as f:
#     while True:
#         try:
#             aa=pickle.load(f)
#             print(aa)
#         except EOFError:
#             break
