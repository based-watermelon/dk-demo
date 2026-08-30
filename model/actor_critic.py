import torch
import torch.nn as nn


STATE_DIM = 503
N_ACTIONS = 7


class ActorCritic(nn.Module):
    def __init__(self):
        super().__init__()

        # Shared feature extractor
        self.shared = nn.Sequential(
            nn.Linear(STATE_DIM, 256),
            nn.ReLU(),

            nn.Linear(256, 128),
            nn.ReLU()
        )

        # Actor: predicts the 7 possible actions
        self.actor = nn.Linear(128, N_ACTIONS)

        # Critic: estimates how good the current state is
        self.critic = nn.Linear(128, 1)

    def forward(self, state):
        features = self.shared(state)

        action_logits = self.actor(features)
        state_value = self.critic(features)

        return action_logits, state_value

    def load_bc_weights(self, bc_path):
        bc_state = torch.load(bc_path, map_location="cpu")

        self.shared[0].weight.data.copy_(bc_state["net.0.weight"])
        self.shared[0].bias.data.copy_(bc_state["net.0.bias"])

        self.shared[2].weight.data.copy_(bc_state["net.3.weight"])
        self.shared[2].bias.data.copy_(bc_state["net.3.bias"])

        self.actor.weight.data.copy_(bc_state["net.6.weight"])
        self.actor.bias.data.copy_(bc_state["net.6.bias"])

    def get_action(self, state):
        action_logits, state_value = self.forward(state)

        probabilities = torch.softmax(action_logits, dim=-1)

        distribution = torch.distributions.Categorical(probabilities)

        action = distribution.sample()

        return action.item(), state_value