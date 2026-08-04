import hre from "hardhat";

async function main() {
  console.log("Deploying ThreatChainVault...");
  const Vault = await hre.ethers.getContractFactory("ThreatChainVault");
  const vault = await Vault.deploy();
  await vault.waitForDeployment();

  const address = await vault.getAddress();
  console.log("ThreatChainVault deployed to:", address);
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
