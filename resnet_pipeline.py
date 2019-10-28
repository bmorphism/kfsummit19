import kfp
import kfp.dsl as dsl
from kfp.components import func_to_container_op
from kfp.onprem import mount_pvc

c= kfp.Client("127.0.0.1:8082/pipeline", namespace="kfsummit")

def PreprocessOp(name, input_dir, output_dir):
    return dsl.ContainerOp(
        name=name,
        image='eu.gcr.io/kfsummit/preprocess_resnet',
        arguments=[
            '--input_dir', input_dir,
            '--output_dir', output_dir,
        ],
        file_outputs={'output': '/output.txt'}
    )

def TrainOp(name, input_dir, output_dir, model_name, model_version, epochs):
    return dsl.ContainerOp(
        name=name,
        image='eu.gcr.io/kfsummit/train_resnet',
        arguments=[
            '--input_dir', input_dir,
            '--output_dir', output_dir,
            '--model_name', model_name,
            '--model_version', model_version,
            '--epochs', epochs
        ],
        file_outputs={'output': '/output.txt'}
    )

@dsl.pipeline(
    name='resnet_cifar10_pipeline',
    description='Demonstrate an end-to-end training & serving pipeline using ResNet and CIFAR-10'
)
def resnet_pipeline(
    raw_data_dir='/mnt/workspace/raw_data',
    processed_data_dir='/mnt/workspace/processed_data',
    model_dir='/mnt/workspace/saved_model',
    epochs=50,
    trtserver_name='trtis',
    model_name='resnet_graphdef',
    model_version=1,
    webapp_prefix='webapp',
    webapp_port=80
):
    pvc_name = 'kfsummit-workspace-read-claim'
    volume_name = 'kfsummit-workspace'
    volume_mount_path = '/mnt/workspace'

    op_dict = {}

    op_dict['preprocess'] = PreprocessOp(
        'preprocess', raw_data_dir, processed_data_dir)

    op_dict['train'] = TrainOp(
	'train', op_dict['preprocess'].output, model_dir, model_name, model_version, epochs)

    for _, container_op in op_dict.items():
        container_op.apply(mount_pvc(pvc_name, volume_name, volume_mount_path))