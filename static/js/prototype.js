const nodeConfig = {
    coordinator: {
        title: 'Nodo Coordinador Central',
        subtitle: 'Supervisión logística nacional y consolidación analítica',
        label: 'SUPERVISIÓN NACIONAL',
        accent: 'ACENTO DE COORDINACIÓN',
        activePanel: 'coordinator-panel'
    },
    lapaz: {
        title: 'Nodo Regional La Paz',
        subtitle: 'Gestión operativa de transmisiones occidente',
        label: 'MOTOR POSTGRESQL',
        accent: 'REGIÓN ORIENTADA',
        activePanel: 'lapaz-panel'
    },
    scz: {
        title: 'Nodo Regional Santa Cruz',
        subtitle: 'Gestión operativa de transmisiones oriente',
        label: 'MOTOR SQL SERVER',
        accent: 'REGIÓN ORIENTADA',
        activePanel: 'scz-panel'
    }
};

function setActiveNode(nodeKey) {
    const sidebarItems = document.querySelectorAll('.sidebar-item');
    sidebarItems.forEach(item => {
        item.classList.toggle('active', item.dataset.node === nodeKey);
    });

    const panels = document.querySelectorAll('.node-panel');
    panels.forEach(panel => {
        panel.classList.toggle('hidden', panel.dataset.node !== nodeKey);
    });

    const config = nodeConfig[nodeKey];
    document.getElementById('node-title').innerText = config.title;
    document.getElementById('node-subtitle').innerText = config.subtitle;
    document.getElementById('node-label').innerText = config.label;
    document.getElementById('node-accent').innerText = config.accent;
    document.getElementById('active-node').innerText = config.title;
    document.getElementById('active-node-status').innerText = nodeKey === 'coordinator' ? 'Modo Supervisor' : 'Modo Local';
    document.getElementById('feedback-message').innerText = 'Seleccionado: ' + config.title + '. Navegue por las acciones disponibles.';
}

function handleAction(actionName) {
    document.getElementById('feedback-message').innerText = `Acción ejecutada: ${actionName}`;
    const timestamp = new Date().toLocaleTimeString('es-BO', { hour12: false });
    const log = document.getElementById('action-log');
    const entry = document.createElement('div');
    entry.className = 'feedback-entry';
    entry.textContent = `[${timestamp}] ${actionName}`;
    log.prepend(entry);
}

function attachActionHandlers() {
    const actionButtons = document.querySelectorAll('[data-action]');
    actionButtons.forEach(button => {
        button.addEventListener('click', () => {
            handleAction(button.dataset.action);
        });
    });
}

window.addEventListener('DOMContentLoaded', () => {
    attachActionHandlers();
    const sidebarButtons = document.querySelectorAll('.sidebar-item');
    sidebarButtons.forEach(button => {
        button.addEventListener('click', () => setActiveNode(button.dataset.node));
    });
    setActiveNode('coordinator');
});