from starlette.applications import Starlette
from starlette.responses import HTMLResponse, JSONResponse
from starlette.staticfiles import StaticFiles
from starlette.middleware.cors import CORSMiddleware
import uvicorn, aiohttp, asyncio
from io import BytesIO

from fastai import *
from fastai.vision import *
torch.nn.Module.dump_patches = True

# HELP VAR SETUP
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 
# get file from google drive
# export_file_url = 'https://www.dropbox.com/s/v6cuuvddq73d1e0/export.pkl?raw=1'
export_file_url = 'https://drive.google.com/uc?export=download&id=1AdguMxQo0xvAVBAvp-zOpVGFlNT27bu-'
export_file_name = 'export.pkl'
# define classes
classes = ['black', 'grizzly', 'teddys']

# get current file path
path = Path(__file__).parent


# BUILD SERVER
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 
app = Starlette()
app.add_middleware(CORSMiddleware, allow_origins=['*'], 
                                    allow_headers=['X-Requested-With', 'Content-Type'])
app.mount('/static', StaticFiles(directory='app/static'))

# CREATE FUNCTION
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 
# download file..
async def download_file(url, dest):
    if dest.exists(): return   # check if it exist
    # if not, create session, get url and use repsonse read to get data and write
    async with aiohttp.ClientSession() as session:  
        async with session.get(url) as response:
            data = await response.read()
            with open(dest, 'wb') as f: f.write(data)

# setup learner, get model, and use load_learner to read to path.file
async def setup_learner():
    await download_file(export_file_url, path/export_file_name)
    try:
        learn = load_learner(path, export_file_name)
        return learn
    except RuntimeError as e:
        if len(e.args) > 0 and 'CPU-only machine' in e.args[0]:
            print(e)
            message = "\n\nThis model was trained with an old version of fastai and will not work in a CPU environment.\n\nPlease update the fastai library in your training environment and export your model again.\n\nSee instructions for 'Returning to work' at https://course.fast.ai."
            raise RuntimeError(message)
        else:
            raise


# LOOP LEANER
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 
# get loop instance
loop = asyncio.get_event_loop()
# 将 setup_learner coroutine 打包为一个 Task 排入日程准备执行。返回 Task 对象
tasks = [asyncio.ensure_future(setup_learner())]
learn = loop.run_until_complete(asyncio.gather(*tasks))[0]
loop.close()


# DEINFE PATH
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 
# Http get request to "/", go back to homepage
@app.route('/')
def index(request):
    html = path/'view'/'index.html'
    return HTMLResponse(html.open(encoding="utf-8").read())

# Http POST request to '/analyze'
# get data -> read data into imgage byte -> open image
# --> use learn to predict -> send the prediction via Json
@app.route('/analyze', methods=['POST'])
async def analyze(request):
    data = await request.form()
    img_bytes = await (data['file'].read())
    img = open_image(BytesIO(img_bytes))
    prediction = learn.predict(img)[0]
    return JSONResponse({'result': str(prediction)})

if __name__ == '__main__':
    if 'serve' in sys.argv: uvicorn.run(app=app, host='0.0.0.0', port=5042)