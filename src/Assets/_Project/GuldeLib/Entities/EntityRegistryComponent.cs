using System;
using System.Collections.Generic;
using MonoLogger.Runtime;
using Sirenix.OdinInspector;

namespace GuldeLib.Entities
{
    public class EntityRegistryComponent : SerializedMonoBehaviour
    {
        [ShowInInspector]
        [BoxGroup("Info")]
        public HashSet<EntityComponent> Entities { get; } = new HashSet<EntityComponent>();

        public event EventHandler<EntityEventArgs> Registered;
        public event EventHandler<EntityEventArgs> Unregistered;

        public bool IsRegistered(EntityComponent entityComponent) => Entities.Contains(entityComponent);

        public void Register(EntityComponent entity)
        {
            if (!entity) return;

            this.Log($"Registry registering entity {entity}");

            Entities.Add(entity);

            Registered?.Invoke(this, new EntityEventArgs(entity));
        }

        public void Unregister(EntityComponent entity)
        {
            if (!entity) return;

            this.Log($"Registry unregistering entity {entity}");

            Entities.Remove(entity);

            Unregistered?.Invoke(this, new EntityEventArgs(entity));
        }
    }
}