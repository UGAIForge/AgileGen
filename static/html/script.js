
document.getElementById('create-alliance-form').addEventListener('submit', function(e) {
    e.preventDefault();
    const allianceName = document.getElementById('alliance-name').value;
    const allianceDescription = document.getElementById('alliance-description').value;
    document.getElementById('create-alliance-status').innerText = `Alliance "${allianceName}" created successfully!`;
});

document.getElementById('invite-players-form').addEventListener('submit', function(e) {
    e.preventDefault();
    const playerUsername = document.getElementById('player-username').value;
    document.getElementById('invite-players-status').innerText = `Invitation sent to ${playerUsername}!`;
});

document.getElementById('launch-attack-form').addEventListener('submit', function(e) {
    e.preventDefault();
    const targetTerritory = document.getElementById('target-territory').value;
    const allocateTroops = document.getElementById('allocate-troops').value;
    document.getElementById('launch-attack-status').innerText = `Attack launched on ${targetTerritory} with ${allocateTroops} troops!`;
});

document.getElementById('allocate-resources-form').addEventListener('submit', function(e) {
    e.preventDefault();
    const initialResources = 5000;
    const requiredResources = parseInt(document.getElementById('required-resources').value);
    const remainingResources = initialResources - requiredResources;
    document.getElementById('allocate-resources-status').innerText = `Remaining Resources: ${remainingResources}`;
});
