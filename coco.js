/**
 * @license
 * Copyright 2018 Google Inc. All Rights Reserved.
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 * https://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 * =============================================================================
 */
import * as posenet from '@tensorflow-models/posenet';
import * as tf from '@tensorflow/tfjs';
import dat from 'dat.gui';

// clang-format off
import {
  drawBoundingBox,
  drawKeypoints,
  drawPoint,
  drawSegment,
  drawSkeleton,
  renderImageToCanvas,
} from './demo_util';

// clang-format on


const images = [
  'frisbee.jpg',
  'frisbee_2.jpg',
  'backpackman.jpg',
  'boy_doughnut.jpg',
  'soccer.png',
  'with_computer.jpg',
  'snowboard.jpg',
  'person_bench.jpg',
  'skiing.jpg',
  'fire_hydrant.jpg',
  'kyte.jpg',
  'looking_at_computer.jpg',
  'tennis.jpg',
  'tennis_standing.jpg',
  'truck.jpg',
  'on_bus.jpg',
  'tie_with_beer.jpg',
  'baseball.jpg',
  'multi_skiing.jpg',
  'riding_elephant.jpg',
  'skate_park_venice.jpg',
  'skate_park.jpg',
  'tennis_in_crowd.jpg',
  'two_on_bench.jpg',
  'perfectplank.PNG'
];

const { partIds, poseChain } = posenet;

/**
 * Draws a pose if it passes a minimum confidence onto a canvas.
 * Only the pose's keypoints that pass a minPartConfidence are drawn.
 */
function drawResults(canvas, poses, minPartConfidence, minPoseConfidence) {
  renderImageToCanvas(image, [513, 513], canvas);
  poses.forEach((pose) => {
    if (pose.score >= minPoseConfidence) {
      let keypointLocations = {}
      pose.keypoints.forEach(function (keypoint) {
        keypointLocations[keypoint.part] = keypoint.position
      });
      console.log(pose.keypoints)
      let angle = calculateAngles(keypointLocations)
      document.getElementById('textp').innerHTML = angle
      console.log(angle)
      // var ctx = canvas.getContext('2d')
      // ctx.beginPath();
      // ctx.arc(drawDetails.keyPoints["leftHip"].x, drawDetails.keyPoints["leftHip"].y, 10, 0, Math.PI * 2);
      // ctx.stroke();
      if (guiState.showKeypoints) {
        drawKeypoints(
          pose.keypoints, minPartConfidence, canvas.getContext('2d'));
      }

      if (guiState.showSkeleton) {
        drawSkeleton(
          pose.keypoints, minPartConfidence, canvas.getContext('2d'));
      }

      if (guiState.showBoundingBox) {
        drawBoundingBox(pose.keypoints, canvas.getContext('2d'));
      }
    }
  });
}

function calculateAngles(keypointLocations) {

  let angleDhruv = getAngle("Shoulder", "Hip", "Knee", keypointLocations)
  return angleDhruv;
  //let angle = getAngle("Shoulder", "Hip", "Knee", keypointLocations)
  //console.log(angle);
  // console.log("shk " + angleDhruv);

  // // let triplets = "Elbow", "Shoulder", "Hip"

  // let tripletAngle = getAngle("Elbow", "Shoulder", "Hip", keypointLocations)

  return { "keypoints": keypointLocations };
  console.log("esh " + tripletAngle)

  var tripletAngle1 = getAngle("Wrist", "Elbow", "Shoulder", keypointLocations)
  console.log("wes " + tripletAngle1)
}

function getAngle(part1, part2, part3, keypointLocations) {
  let x1 = keypointLocations["left" + part1].x
  let x2 = keypointLocations["left" + part2].x
  let x3 = keypointLocations["left" + part3].x

  let y1 = -keypointLocations["left" + part1].y
  let y2 = -keypointLocations["left" + part2].y
  let y3 = -keypointLocations["left" + part3].y
  console.log("({0},{1}), ({2},{3}), ({4}, {5})", x1, y1, x2, y2, x3, y3)
  let m1 = ((y1 - y2) / (x1 - x2))
  let m2 = ((y2 - y3) / (x2 - x3))

  if (Math.atan(m1) < Math.atan(m2)) {
    var m3 = m1;
    m1 = m2;
    m2 = m3;
  }
  // if (m1 < 0) {
  //   m1 = Math.PI + m1;
  // }
  // if (m2 < 0) {
  //   m2 = Math.PI + m2;
  // }
  // console.log("atan m1 = " + m1)
  // if (m1 < 0) {
  //   m1 = Math.PI + m1;
  // }
  // console.log("jsafkdlsjfl ", m1 - m2)
  // console.log("M slope " + ((m1 - m2) / (1 + m1 * m2)))
  var m = 180 - ((Math.atan(Math.abs((m2 - m1) / (1 + m1 * m2))) * 180) / Math.PI);
  // console.log("M1 radians " + m1)
  // console.log("M1" + 180 * (m1) / Math.PI)
  // console.log("M2" + 180 * (m2) / Math.PI)
  return m;
}

function getAngleShivam(part1, part2, part3, keypointLocations) {
  let x1 = keypointLocations["left" + part1].x
  let x2 = keypointLocations["left" + part2].x
  let x3 = keypointLocations["left" + part3].x

  let y1 = keypointLocations["left" + part1].y
  let y2 = keypointLocations["left" + part2].y
  let y3 = keypointLocations["left" + part3].y
  let m = Math.atan(Math.sqrt(Math.pow((x1 - x2), 2) + Math.pow((y1 - y2), 2)) / Math.sqrt(Math.pow((x3 - x2), 2) + Math.pow((y3 - y2), 2)))
  return m * 180 / Math.PI;
}

function getAngleMayank(part1, part2, part3, keypointLocations) {
  let x1 = keypointLocations["left" + part1].x
  let x2 = keypointLocations["left" + part2].x
  let x3 = keypointLocations["left" + part3].x

  let y1 = keypointLocations["left" + part1].y
  let y2 = keypointLocations["left" + part2].y
  let y3 = keypointLocations["left" + part3].y
  let m1 = Math.atan(Math.abs(Math.abs(y1 - y2) / Math.abs(x1 - x2)))
  let m2 = Math.atan(Math.abs(Math.abs(y2 - y3) / Math.abs(x2 - x3)))
  //return m1 + m2;
  console.log("Mayank m1 " + ((180 * m1) / Math.PI))
  console.log("Mayank m2 " + ((180 * m2) / Math.PI))
  return ((180 * m1) / Math.PI) + ((180 * m2) / Math.PI);
}


const imageBucket =
  'https://storage.googleapis.com/tfjs-models/assets/posenet/';

async function loadImage(imagePath) {
  var image = document.getElementById('img2');;
  const promise = new Promise((resolve, reject) => {
    resolve(image);
    // image.crossOrigin = '';
    // image.onload = () => {
    //   // console.log(image.height);
    //   // console.log(image.width);
    //   image.height = 513;
    //   image.width = 513;
    //   // image.height = "533";
    //   // image.width = "533";
    //   // console.log(image.width);
    //   // console.log(image.height);
    //   resolve(image);
    // };
  });

  // image.src = `${imageBucket}${imagePath}`;
  // if (imagePath == 'perfectplank.PNG') {
  //   image.src = 'https://i.ibb.co/vcnk6NG/whatsapp-image-2019-05-13-at-1.jpg';
  //   // image.src = 'https://i.ibb.co/yPNPT5X/planknew2-1.jpg';
  // }
  // else {
  //   image.src = `${imageBucket}${imagePath}`;
  // }
  // image =
  return promise;
}

function singlePersonCanvas() {
  return document.querySelector('#single canvas');
}

function multiPersonCanvas() {
  return document.querySelector('#multi canvas');
}

/**
 * Draw the results from the single-pose estimation on to a canvas
 */
function drawSinglePoseResults(pose) {
  const canvas = singlePersonCanvas();
  drawResults(
    canvas, [pose], guiState.singlePoseDetection.minPartConfidence,
    guiState.singlePoseDetection.minPoseConfidence);

  const { part, showHeatmap, showOffsets } = guiState.visualizeOutputs;
  // displacements not used for single pose decoding
  const showDisplacements = false;
  const partId = +part;

  visualizeOutputs(
    partId, showHeatmap, showOffsets, showDisplacements,
    canvas.getContext('2d'));
}

/**
 * Draw the results from the multi-pose estimation on to a canvas
 */
function drawMultiplePosesResults(poses) {
  const canvas = multiPersonCanvas();
  drawResults(
    canvas, poses, guiState.multiPoseDetection.minPartConfidence,
    guiState.multiPoseDetection.minPoseConfidence);

  const { part, showHeatmap, showOffsets, showDisplacements } =
    guiState.visualizeOutputs;
  const partId = +part;

  visualizeOutputs(
    partId, showHeatmap, showOffsets, showDisplacements,
    canvas.getContext('2d'));
}

/**
 * Define the skeleton by part id. This is used in multi-pose estimation. This
 *defines the parent->child relationships of our tree. Arbitrarily this defines
 *the nose as the root of the tree.
 **/
const parentChildrenTuples = poseChain.map(
  ([parentJoinName, childJoinName]) =>
    ([partIds[parentJoinName], partIds[childJoinName]]));

/**
 * Parent to child edges from the skeleton indexed by part id.  Indexes the edge
 * ids by the part ids.
 */
const parentToChildEdges =
  parentChildrenTuples.reduce((result, [partId], i) => {
    if (result[partId]) {
      result[partId] = [...result[partId], i];
    } else {
      result[partId] = [i];
    }

    return result;
  }, {});

/**
 * Child to parent edges from the skeleton indexed by part id.  Indexes the edge
 * ids by the part ids.
 */
const childToParentEdges =
  parentChildrenTuples.reduce((result, [, partId], i) => {
    if (result[partId]) {
      result[partId] = [...result[partId], i];
    } else {
      result[partId] = [i];
    }

    return result;
  }, {});


function drawOffsetVector(
  ctx, y, x, outputStride, offsetsVectorY, offsetsVectorX) {
  drawSegment(
    [y * outputStride, x * outputStride],
    [y * outputStride + offsetsVectorY, x * outputStride + offsetsVectorX],
    'red', 1., ctx);
}

function drawDisplacementEdgesFrom(
  ctx, partId, displacements, outputStride, edges, y, x, offsetsVectorY,
  offsetsVectorX) {
  const numEdges = displacements.shape[2] / 2;

  const offsetX = x * outputStride + offsetsVectorX;
  const offsetY = y * outputStride + offsetsVectorY;

  const edgeIds = edges[partId] || [];

  if (edgeIds.length > 0) {
    const displArr = displacements.arraySync();
    edgeIds.forEach((edgeId) => {
      const displacementY = displArr[y][x][edgeId];
      const displacementX = displArr[y][x][edgeId + numEdges];

      drawSegment(
        [offsetY, offsetX],
        [offsetY + displacementY, offsetX + displacementX], 'blue', 1., ctx);
    });
  }
}

/**
 * Visualizes the outputs from the model which are used for decoding poses.
 * Limited to visualizing the outputs for a single part.
 *
 * @param partId The id of the part to visualize
 *
 */
function visualizeOutputs(
  partId, drawHeatmaps, drawOffsetVectors, drawDisplacements, ctx) {
  const { heatmapScores, offsets, displacementFwd, displacementBwd } =
    modelOutputs;
  const outputStride = +guiState.outputStride;

  const [height, width] = heatmapScores.shape;

  ctx.globalAlpha = 0;
  const heatmapScoresArr = heatmapScores.arraySync();
  const offsetsArr = offsets.arraySync();

  for (let y = 0; y < height; y++) {
    for (let x = 0; x < width; x++) {
      const score = heatmapScoresArr[y][x][partId];

      // to save on performance, don't draw anything with a low score.
      if (score < 0.05) continue;

      // set opacity of drawn elements based on the score
      ctx.globalAlpha = score;

      if (drawHeatmaps) {
        drawPoint(ctx, y * outputStride, x * outputStride, 2, 'yellow');
      }

      const offsetsVectorY = offsetsArr[y][x][partId];
      const offsetsVectorX = offsetsArr[y][x][partId + 17];

      if (drawOffsetVectors) {
        drawOffsetVector(
          ctx, y, x, outputStride, offsetsVectorY, offsetsVectorX);
      }

      if (drawDisplacements) {
        // exponentially affect the alpha of the displacements;
        ctx.globalAlpha *= score;

        drawDisplacementEdgesFrom(
          ctx, partId, displacementFwd, outputStride, parentToChildEdges, y,
          x, offsetsVectorY, offsetsVectorX);

        drawDisplacementEdgesFrom(
          ctx, partId, displacementBwd, outputStride, childToParentEdges, y,
          x, offsetsVectorY, offsetsVectorX);
      }
    }

    ctx.globalAlpha = 1;
  }
}

/**
 * Converts the raw model output results into single-pose estimation results
 */
async function decodeSinglePoseAndDrawResults() {
  if (!modelOutputs) {
    return;
  }

  const pose = await posenet.decodeSinglePose(
    modelOutputs.heatmapScores, modelOutputs.offsets, guiState.outputStride);

  drawSinglePoseResults(pose);
}

/**
 * Converts the raw model output results into multi-pose estimation results
 */
async function decodeMultiplePosesAndDrawResults() {
  if (!modelOutputs) {
    return;
  }

  const poses = await posenet.decodeMultiplePoses(
    modelOutputs.heatmapScores, modelOutputs.offsets,
    modelOutputs.displacementFwd, modelOutputs.displacementBwd,
    guiState.outputStride, guiState.multiPoseDetection.maxDetections,
    guiState.multiPoseDetection);

  drawMultiplePosesResults(poses);
}

function decodeSingleAndMultiplePoses() {
  decodeSinglePoseAndDrawResults();
  decodeMultiplePosesAndDrawResults();
}

function setStatusText(text) {
  const resultElement = document.getElementById('status');
  resultElement.innerText = text;
}

let image = null;
let modelOutputs = null;

/**
 * Purges variables and frees up GPU memory using dispose() method
 */
function disposeModelOutputs() {
  if (modelOutputs) {
    modelOutputs.heatmapScores.dispose();
    modelOutputs.offsets.dispose();
    modelOutputs.displacementFwd.dispose();
    modelOutputs.displacementBwd.dispose();
  }
}

/**
 * Loads an image, feeds it into posenet the posenet model, and
 * calculates poses based on the model outputs
 */
async function testImageAndEstimatePoses(net) {
  setStatusText('Predicting...');
  document.getElementById('results').style.display = 'none';

  // Purge prevoius variables and free up GPU memory
  disposeModelOutputs();

  // Load an example image
  image = await loadImage(guiState.image);
  document.body.appendChild(image);
  // Creates a tensor from an image
  const input = tf.browser.fromPixels(image);

  // Stores the raw model outputs from both single- and multi-pose results can
  // be decoded.
  // Normally you would call estimateSinglePose or estimateMultiplePoses,
  // but by calling this method we can previous the outputs of the model and
  // visualize them.
  modelOutputs = await net.predictForMultiPose(input, guiState.outputStride);

  // Process the model outputs to convert into poses
  await decodeSingleAndMultiplePoses();

  setStatusText('');
  document.getElementById('results').style.display = 'block';
  input.dispose();
}

let guiState;

function setupGui(net) {
  guiState = {
    outputStride: 8,
    image: 'perfectplank.PNG',
    detectPoseButton: () => {
      testImageAndEstimatePoses(net);
    },
    singlePoseDetection: {
      minPartConfidence: 0.5,
      minPoseConfidence: 0.5,
    },
    multiPoseDetection: {
      minPartConfidence: 0.5,
      minPoseConfidence: 0.5,
      scoreThreshold: 0.5,
      nmsRadius: 20.0,
      maxDetections: 15,
    },
    showKeypoints: true,
    showSkeleton: true,
    showBoundingBox: false,
    visualizeOutputs: {
      part: 0,
      showHeatmap: false,
      showOffsets: false,
      showDisplacements: false,
    },
  };

  const gui = new dat.GUI();
  // Output stride:  Internally, this parameter affects the height and width of
  // the layers in the neural network. The lower the value of the output stride
  // the higher the accuracy but slower the speed, the higher the value the
  // faster the speed but lower the accuracy.
  gui.add(guiState, 'outputStride', [8, 16, 32]).onChange((outputStride) => {
    guiState.outputStride = +outputStride;
    testImageAndEstimatePoses(net);
  });
  gui.add(guiState, 'image', images)
    .onChange(() => testImageAndEstimatePoses(net));

  // Pose confidence: the overall confidence in the estimation of a person's
  // pose (i.e. a person detected in a frame)
  // Min part confidence: the confidence that a particular estimated keypoint
  // position is accurate (i.e. the elbow's position)

  const multiPoseDetection = gui.addFolder('Multi Pose Estimation');
  multiPoseDetection.open();
  multiPoseDetection
    .add(guiState.multiPoseDetection, 'minPartConfidence', 0.0, 1.0)
    .onChange(decodeMultiplePosesAndDrawResults);
  multiPoseDetection
    .add(guiState.multiPoseDetection, 'minPoseConfidence', 0.0, 1.0)
    .onChange(decodeMultiplePosesAndDrawResults);

  // nms Radius: controls the minimum distance between poses that are returned
  // defaults to 20, which is probably fine for most use cases
  multiPoseDetection.add(guiState.multiPoseDetection, 'nmsRadius', 0.0, 40.0)
    .onChange(decodeMultiplePosesAndDrawResults);
  multiPoseDetection.add(guiState.multiPoseDetection, 'maxDetections')
    .min(1)
    .max(20)
    .step(1)
    .onChange(decodeMultiplePosesAndDrawResults);

  const singlePoseDetection = gui.addFolder('Single Pose Estimation');
  singlePoseDetection
    .add(guiState.singlePoseDetection, 'minPartConfidence', 0.0, 1.0)
    .onChange(decodeSinglePoseAndDrawResults);
  singlePoseDetection
    .add(guiState.singlePoseDetection, 'minPoseConfidence', 0.0, 1.0)
    .onChange(decodeSinglePoseAndDrawResults);
  singlePoseDetection.open();

  gui.add(guiState, 'showKeypoints').onChange(decodeSingleAndMultiplePoses);
  gui.add(guiState, 'showSkeleton').onChange(decodeSingleAndMultiplePoses);
  gui.add(guiState, 'showBoundingBox').onChange(decodeSingleAndMultiplePoses);

  const visualizeOutputs = gui.addFolder('Visualize Outputs');

  visualizeOutputs.add(guiState.visualizeOutputs, 'part', posenet.partIds)
    .onChange(decodeSingleAndMultiplePoses);
  visualizeOutputs.add(guiState.visualizeOutputs, 'showHeatmap')
    .onChange(decodeSingleAndMultiplePoses);
  visualizeOutputs.add(guiState.visualizeOutputs, 'showOffsets')
    .onChange(decodeSingleAndMultiplePoses);
  visualizeOutputs.add(guiState.visualizeOutputs, 'showDisplacements')
    .onChange(decodeSingleAndMultiplePoses);

  visualizeOutputs.open();
}

/**
 * Kicks off the demo by loading the posenet model and estimating
 * poses on a default image
 */
export async function bindPage() {
  const net = await posenet.load();

  setupGui(net);

  await testImageAndEstimatePoses(net);
  document.getElementById('loading').style.display = 'none';
  document.getElementById('main').style.display = 'block';
}

bindPage();
