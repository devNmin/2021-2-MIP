import cv2
import os
import torch
import torch.nn.functional as F
import numpy as np
import transforms_mod as tt
import torchvision
import transforms
from movinets import MoViNet
from movinets.config import _C
import PIL
#filePath='/home/ssslab/Downloads/videos/A_Fall_1.mp4'
#filePath='/home/ssslab/Downloads/videos/A_faint_1.mp4'
#filePath="./data_clip_Falls/완료_0910_H_실신_CAM1_24_masking.mp4"
f= "/home/ssslab/Desktop/Dataset/cctv_data/cubox_cctv_data/faint/"
filePath=f+'완료_0910_H_실신_CAM2_44_masking.mp4'

print(filePath)

model = MoViNet(_C.MODEL.MoViNetA0, causal = False, pretrained = True )
model.classifier[3] = torch.nn.Conv3d(2048, 2, (1,1,1))

model.load_state_dict(torch.load('./model_data/class2/Movinet_class2_pre_faint_5.pth'))
#model.load_state_dict(torch.load('./model_data/class2/Movinet_class2_preno_Fall_9.pth'))

# video_capture = cv2.VideoCapture(filePath)

model.cuda()
model.eval()

model.clean_activation_buffers()

frame_count = 0

org=(550,150)
font=cv2.FONT_HERSHEY_SIMPLEX 
 
flag=0
z=[]
p=[]
cap = cv2.VideoCapture(filePath)

fourcc = cv2.VideoWriter_fourcc(*'DIVX')

height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
out = cv2.VideoWriter('last3.avi', fourcc, 30.0, (int(width), int(height)))
fps=30
normal_cnt=0
Fall_cnt=0
a_cnt=0
pre_frame=0
cur_frame=0
max_len=16
channels=3
padding_mode='last'
n=16
text=''
ff = torch.FloatTensor(3, 500, height, width)
fa = torch.FloatTensor(3, 500, height, width)
text_c=(255,0,0)
text="Normal"
frames = torch.FloatTensor(3, n, height, width)
while cap.isOpened():
    ret, frame = cap.read()

    if ret:
        # print(frame.shape)
        frame_org=frame

        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)  
        frame = torch.from_numpy(frame)
    #         # (H x W x C) to (C x H x W)
        frame = frame.permute(2, 0, 1)
        frames[:,frame_count%n, :, :] = frame.float()
        last_idx=frame_count
        start_idx=last_idx-16
        ff[:,frame_count, :, :] = frame.float()
        
        if frame_count>16:
            fa=ff[:,start_idx:last_idx, :, :]

        frame_count=frame_count+1



        if frame_count%(n-1)==0:
            # ff=
            # ff=ff/255
            # fa=fa/255
            # frame/255
            # frames /= 255
            w=172
            h=172
            # h, w = self.size
            # print(frames.shape)
            C, L, H, W = frames.size()

            rescaled_video = torch.FloatTensor(C, L, h, w)
                    
                    # use torchvision implemention to resize video frames
            transform = torchvision.transforms.Compose([
                        torchvision.transforms.ToPILImage(),
                        torchvision.transforms.Resize((172,172), PIL.Image.BILINEAR),
                        torchvision.transforms.ToTensor(),
                    ])

            for l in range(L):
                frame = rescaled_video[:, (l), :, :]
                frame = transform(frame)
                rescaled_video[:, l, :, :] = frame
            #rescaled_video[:,,:,:]
            rescaled_vide = rescaled_video[:, -1:-1*(n-1), :, :]

            #frames = transform(frames)
            rescaled_video=rescaled_video.reshape(1,3,n,172,172)
            #print(rescaled_video)
            #ff=ff[:,-16::,:,:]
            output= F.log_softmax(model(rescaled_video.cuda()), dim=1) 
            _, pred = torch.max(output, dim=1) 
            print(pred)
            if (pred==1): #Fall
                #text="Fall"
                Fall_cnt=Fall_cnt+1
                cur_frame=1
                # text_c=(255,0,0)
                # cv2.putText(frame_org,str(text),org,font,2,text_c,2)
    
            elif (pred==0 & flag==0): #normal
                text="Normal"
                normal_cnt=normal_cnt+1
                cur_frame=0
                text_c=(255,0,0)
                # cv2.putText(frame_org,str(text),org,font,2,text_c,2)
        #print("fa",Fall_cnt)
            # print("fff",Fall_cnt)
            # if(Fall_cnt>5 & cur_frame==1 & pre_frame==1):
            if(Fall_cnt>5 ):    
                flag==1
                # print("asdasd")
                text="Fall"
                text_c=(0,0,255)
                a_cnt=a_cnt+1
                # Fall_cnt=0
                if (a_cnt>10):

                    print("aaaaa")
                    text="normal" 
                    text_c=(255,0,0)
                   
                    Fall_cnt=0
            else:
                flag=0
            pre_frame=cur_frame

    
            #frame_count=0
    cv2.putText(frame_org,str(text),org,font,3,text_c,8)
    cv2.imshow("image",frame_org)
    out.write(frame_org) 
    if cv2.waitKey(33) ==ord('q'):
        break
cap.release()
out.release()
cv2.destroyAllWindows()
            # z=[]
print(normal_cnt,Fall_cnt)
# cv2.waitKey(3)



