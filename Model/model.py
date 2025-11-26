#finetune ConvNeXt
import timm
import torch.nn as nn
import gdown
import torch

class LocationTemporalClassifier(nn.Module):
    def __init__(self, num_species=854):
      super().__init__()

      #fully connected classifier using location, date, time
      self.classifier = nn.Sequential(
        nn.Linear(4 + 2 + 2, 256),  #lat sin cos, lon sin cos, day sin cos, hour sin cos
        nn.ReLU(),
        nn.Dropout(0.3),
        nn.Linear(256, 128),
        nn.ReLU(),
        nn.Dropout(0.2),
        nn.Linear(128, num_species)
      )

    def forward(self, catd_encd_metadata):
      #input is all encoded metadata concatenated
      return self.classifier(catd_encd_metadata)


class ConvnextFTClassifier(nn.Module):
    def __init__(self, num_species=854):
        super().__init__()

        #load in convnext
        self.backbone = timm.create_model(
            'convnext_nano.in12k_ft_in1k', #use convnext nano pretrained on imagenet12k and ft on 1k, 15.62M params
            pretrained=True,
            num_classes=0,#remove head
        )

        #head
        backbone_features = self.backbone.num_features #768
        self.classifier = nn.Sequential(
            nn.LayerNorm(backbone_features),
            nn.Dropout(0.2),
            nn.Linear(backbone_features, 512),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(512, num_species)
        )

    def forward(self, image):
        features = self.backbone(image)  #image input with dimensions as #[batch, flattened]
        return self.classifier(features)

class SpeciesClassifier(nn.Module):
  def __init__(self, num_species=854, pretrained=False):
    super().__init__()

    #image classifier
    self.image_classifier = ConvnextFTClassifier(num_species)
    #location, date, time classifier
    self.metadata_classifier = LocationTemporalClassifier(num_species)

    if pretrained:
        self._load_pretrained_model()

  def _load_pretrained_model(self):
    file_id = '1vG0T6FLkJEJBMJjRH1qnJSQFMpRDZ2Vp'
    url = f'https://drive.google.com/uc?id={file_id}'
    path="model_epoch_36.pt"
    gdown.download(url, path, quiet=False)
    DEVICE = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    checkpoint = torch.load(path, map_location=DEVICE)
    self.load_state_dict(checkpoint['model_state_dict'])
    print("Loaded pretrained model weights")


  def forward(self, image, catd_encd_metadata, has_metadata):
    image_output = self.image_classifier(image)
    metadata_output = self.metadata_classifier(catd_encd_metadata)
    metadata_output = metadata_output*has_metadata.unsqueeze(1)
    logits = image_output + metadata_output
    return logits



