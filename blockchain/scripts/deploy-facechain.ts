import { network } from "hardhat";

async function main() {
  const { ethers } = await network.create();
  const FaceChain = await ethers.getContractFactory("FaceChain");
  const faceChain = await FaceChain.deploy();
  await faceChain.waitForDeployment();

  const address = await faceChain.getAddress();
  console.log("FaceChain deployed to:", address);
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});