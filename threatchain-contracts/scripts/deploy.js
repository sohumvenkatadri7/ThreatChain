import hre from "hardhat";
import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

async function main() {
  console.log("Deploying ThreatChainVault...");
  const Vault = await hre.ethers.getContractFactory("ThreatChainVault");
  const vault = await Vault.deploy();
  await vault.waitForDeployment();

  const address = await vault.getAddress();
  console.log("ThreatChainVault deployed to:", address);

  // Automatically sync deployed address to .env files across the project
  try {
    const rootEnv = path.resolve(__dirname, "../../.env");
    const frontendEnv = path.resolve(__dirname, "../../threatchain-frontend/.env");
    const rootContent = `CONTRACT_ADDRESS=${address}\nVITE_CONTRACT_ADDRESS=${address}\n`;
    const frontendContent = `VITE_CONTRACT_ADDRESS=${address}\n`;
    fs.writeFileSync(rootEnv, rootContent);
    fs.writeFileSync(frontendEnv, frontendContent);
    console.log("✅ Synchronized CONTRACT_ADDRESS to .env files automatically!");
  } catch (err) {
    console.warn("⚠️ Could not write to .env files:", err.message);
  }
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
